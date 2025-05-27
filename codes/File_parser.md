Perfect. We'll begin with the first component: building modular file loaders and parsers for Databricks notebooks, YAML configs, MLflow metadata, CSV validation results, image metadata, and directory structure. I’ll create production-grade Python code that emphasizes clarity, reusability, and testing-readiness.

I'll let you know once the initial code module is ready for review before we move on to summarization.


# Databricks ML/NLP Project File Loaders

This section provides modular Python code for loading and parsing various file types commonly found in a Databricks-based ML/NLP project documentation system. Each loader is structured as a separate module (e.g., under a `loaders/` package) with a dedicated class or function to handle a specific file type. The loaders return structured content (either LangChain-compatible `Document` objects or dictionaries with text and metadata). Logging and error handling are included for maintainability. The code is compatible with Python 3.8+ and designed to run on Databricks or a similar environment (no real secrets are included; placeholders are used where appropriate).

## Databricks Notebook Loader

Databricks notebooks can be exported in multiple formats: Databricks archive (`.dbc`), source `.py` files, or Jupyter `.ipynb` files. This loader handles all three cases:

* **`.dbc` archives:** These are binary files possibly containing a collection of notebooks. We use the Databricks CLI to export the archive into its constituent notebooks (requires the CLI to be configured with a token or profile). If the CLI is unavailable, the loader logs an error.
* **`.py` source files:** Databricks notebook exports in `.py` contain special annotated lines. Magic commands (e.g., `%sql`, `%md`) appear as lines prefixed by `# MAGIC`, and cell separations are marked by `# COMMAND ----------`. We strip out these magic prefixes and separators, skipping the actual `%magic` command lines, to recover the original cell contents.
* **`.ipynb` files:** We parse Jupyter notebooks (JSON format) and extract cells. Magic commands at the start of code cells (if any) are removed. Both markdown and code cells are captured.

Each cell from the notebook is returned as a separate document with metadata indicating the source file, cell index, and cell type (code or markdown). This allows the documentation system to maintain the structure of the notebook content.

```python
# File: loaders/databricks_notebook_loader.py

import os
import json
import subprocess
import shutil
import tempfile
import logging

logger = logging.getLogger(__name__)

class DatabricksNotebookLoader:
    """Loader for Databricks notebooks (.dbc, .py, .ipynb). Parses and cleans notebook content."""
    
    def load(self, path: str):
        """
        Load a Databricks notebook from .dbc, .py, or .ipynb, stripping magic commands and structuring cells.
        
        Returns:
            List of Document (or dict) objects, one per notebook cell (with text content and metadata).
        """
        docs = []
        try:
            if path.endswith(".dbc"):
                # .dbc archive: use Databricks CLI to export if available
                if shutil.which("databricks") is None:
                    logger.error(f"Databricks CLI not found. Cannot extract {path}")
                    return []
                # Create temp directory to hold exported notebooks
                with tempfile.TemporaryDirectory() as tempdir:
                    # Export all notebooks in the .dbc to the temp directory (SOURCE format for .py files)
                    cmd = ["databricks", "workspace", "export_dir", path, tempdir]
                    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode != 0:
                        logger.error(f"Databricks CLI export_dir failed for {path}: {result.stderr.strip()}")
                        return []
                    # Recursively load any exported files (which might be .py or .ipynb)
                    for root, _, files in os.walk(tempdir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # recursively use this loader for each extracted notebook file
                            docs.extend(self.load(file_path))
                return docs
            
            elif path.endswith(".py"):
                # Load and parse Databricks source .py notebook
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                cell_lines = []
                cell_index = 0
                for line in lines:
                    # Skip the notebook header and cell separator lines
                    if line.strip().startswith("# Databricks notebook source"):
                        continue
                    if line.strip().startswith("# COMMAND ----------"):
                        # end of a cell; package the accumulated cell_lines into a Document
                        content = "".join(cell_lines).rstrip("\n")
                        if content:
                            # Determine cell type: if any MAGIC lines present, likely a markdown or magic cell, else code
                            cell_type = "markdown" if any(l.strip().startswith("%") or l.strip().startswith("#") for l in cell_lines if l.strip()) and not any(l.strip().startswith("%python") for l in cell_lines) else "code"
                            metadata = {"source": path, "cell_index": cell_index, "type": cell_type}
                            docs.append(self._make_document(content, metadata))
                            cell_index += 1
                        cell_lines = []
                        continue
                    # Process magic lines
                    if line.strip().startswith("# MAGIC"):
                        # Remove the "# MAGIC " prefix
                        magic_content = line.replace("# MAGIC", "").lstrip()
                        # Skip actual magic command (lines that start with '%' after the MAGIC prefix)
                        if magic_content.lstrip().startswith("%"):
                            continue
                        cell_lines.append(magic_content)
                    else:
                        # Regular line (code or comment)
                        cell_lines.append(line)
                # If last cell content exists (file may not end with a COMMAND separator)
                if cell_lines:
                    content = "".join(cell_lines).rstrip("\n")
                    if content:
                        cell_type = "markdown" if any(l.strip().startswith("%") or l.strip().startswith("#") for l in cell_lines if l.strip()) and not any(l.strip().startswith("%python") for l in cell_lines) else "code"
                        metadata = {"source": path, "cell_index": cell_index, "type": cell_type}
                        docs.append(self._make_document(content, metadata))
                return docs
            
            elif path.endswith(".ipynb"):
                # Load Jupyter notebook (Databricks Jupyter export or generic ipynb)
                with open(path, 'r', encoding='utf-8') as f:
                    notebook = json.load(f)
                cells = notebook.get("cells", [])
                cell_index = 0
                for cell in cells:
                    cell_type = cell.get("cell_type", "")
                    source_lines = cell.get("source", [])
                    # In ipynb, source might be a list of lines or a single string
                    if isinstance(source_lines, list):
                        source = "".join(source_lines)
                    else:
                        source = str(source_lines)
                    if cell_type == "code":
                        # Remove leading magic commands (like %md, %sql) if present
                        stripped_lines = []
                        for line in source.splitlines():
                            if line.strip().startswith("%") and not line.strip().startswith("%sh"):
                                # skip magic line (except perhaps shell magic if needed, but skip all here)
                                continue
                            stripped_lines.append(line)
                        content = "\n".join(stripped_lines)
                    else:
                        # For markdown or other cell types, use content as is
                        content = source
                    # Only include non-empty content
                    if content.strip():
                        metadata = {"source": path, "cell_index": cell_index, "type": cell_type}
                        docs.append(self._make_document(content, metadata))
                        cell_index += 1
                return docs
            
            else:
                logger.warning(f"Unsupported file type for DatabricksNotebookLoader: {path}")
                return []
        except Exception as e:
            logger.error(f"Failed to load notebook {path}: {e}")
            return []
    
    def _make_document(self, text: str, metadata: dict):
        """Helper to create a LangChain Document or plain dict with text and metadata."""
        try:
            from langchain.schema import Document
            return Document(page_content=text, metadata=metadata)
        except ImportError:
            # If LangChain not installed, fallback to simple dict
            return {"text": text, "metadata": metadata}
```

**Explanation:** The loader above first handles Databricks archive files by invoking the Databricks CLI to export the archive (which requires prior authentication setup). For `.py` notebooks, it removes lines like `# MAGIC ...` (which denote magic commands and markdown content) and `# COMMAND ----------` (cell separators). Magic command lines (those starting with `%` after removing `# MAGIC`) are skipped, while the rest of the content is accumulated. Each cell's text and type (code or markdown) is inferred and stored in the document metadata. The `.ipynb` case reads the JSON, iterates through cells, and similarly strips out any leading `%` magic commands in code cells. The result is a list of structured documents, each containing content from one cell of the notebook and metadata about that cell.

## YAML Config Loader

YAML configuration files often store experiment settings, model parameters, or pipeline configurations. This loader uses PyYAML (or `ruamel.yaml`) to parse YAML files and returns their content in a structured way. We utilize `yaml.safe_load()` to avoid executing arbitrary tags or objects in the YAML. The loader can either return the raw text or a parsed dictionary; here we demonstrate returning the original text content along with the parsed data in metadata for flexibility.

```python
# File: loaders/yaml_config_loader.py

import logging
import yaml

logger = logging.getLogger(__name__)

class YAMLConfigLoader:
    """Loader for YAML configuration files. Parses YAML content into text and structured data."""
    
    def load(self, path: str):
        """
        Load a YAML file, returning its text content and parsed structure.
        
        Returns:
            A list with one Document (or dict) containing the YAML text and a metadata dict of parsed content.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Failed to read YAML file {path}: {e}")
            return []
        try:
            data = yaml.safe_load(text)  # Parse YAML into Python dict safely
        except Exception as e:
            logger.error(f"YAML parsing error in {path}: {e}")
            data = None
        # Prepare metadata with parsed data (if any)
        metadata = {"source": path}
        if data is not None:
            metadata["parsed"] = data
        # Return as a single-document list
        doc = self._make_document(text, metadata)
        return [doc]
    
    def _make_document(self, text: str, metadata: dict):
        """Create a Document or dict for the YAML content."""
        try:
            from langchain.schema import Document
            return Document(page_content=text, metadata=metadata)
        except ImportError:
            return {"text": text, "metadata": metadata}
```

**Explanation:** The YAML loader reads the entire file as text and then attempts to parse it using PyYAML. We use `yaml.safe_load()` which *“should always be preferred to avoid introducing the possibility for arbitrary code execution”*. If parsing succeeds, the Python dictionary is stored in the document's metadata (`parsed` field), while the `page_content` remains the original YAML text (making it easy to search or display in documentation). Logging is used to report file read errors or YAML syntax issues. The loader returns a list with a single document representing the YAML file.

## MLflow Metadata Loader

Machine learning experiments tracked with MLflow can produce metadata like parameters and metrics for each run. This loader connects to an MLflow Tracking Server (using `mlflow.tracking.MlflowClient`) and fetches experiment or run information. It can summarize an entire experiment (with multiple runs) or a single run. We avoid hard-coding any credentials: the tracking URI can be specified or will default to a Databricks tracking server (using environment variables or a profile). The output is a textual summary of parameters and metrics, which can be useful for documentation or search.

```python
# File: loaders/mlflow_metadata_loader.py

import os
import logging
from mlflow.tracking import MlflowClient

logger = logging.getLogger(__name__)

class MLflowMetadataLoader:
    """Loader for MLflow experiment metadata. Fetches run parameters and metrics via MlflowClient."""
    
    def __init__(self, tracking_uri: str = None):
        """
        Initialize the MLflow client. 
        Args:
            tracking_uri: Optional MLflow tracking URI. If None, will use MLFLOW_TRACKING_URI env or Databricks workspace.
        """
        # Use provided URI or fall back to environment or 'databricks'
        default_uri = os.getenv('MLFLOW_TRACKING_URI', 'databricks')
        self.tracking_uri = tracking_uri or default_uri
        try:
            self.client = MlflowClient(tracking_uri=self.tracking_uri)
        except Exception as e:
            logger.error(f"Failed to initialize MlflowClient with URI {self.tracking_uri}: {e}")
            raise
    
    def load_experiment(self, experiment_id: str = None, experiment_name: str = None):
        """
        Load all runs from an MLflow experiment and return documents summarizing parameters and metrics.
        
        Either experiment_id or experiment_name should be provided.
        Returns:
            List of Document (or dict) objects: one for the experiment summary and one per run.
        """
        # Resolve experiment ID from name if needed
        exp = None
        try:
            if experiment_id:
                exp = self.client.get_experiment(experiment_id)
            elif experiment_name:
                exp = self.client.get_experiment_by_name(experiment_name)
            else:
                logger.error("No experiment_id or experiment_name provided")
                return []
        except Exception as e:
            logger.error(f"Error retrieving experiment info: {e}")
            return []
        if exp is None:
            logger.error(f"Experiment not found (ID={experiment_id}, Name={experiment_name})")
            return []
        
        experiment_id = exp.experiment_id
        experiment_name = exp.name
        docs = []
        # Create a summary for the experiment itself
        summary_lines = []
        summary_lines.append(f"Experiment '{experiment_name}' (ID: {experiment_id})")
        if exp.tags.get("mlflow.note.content"):
            # Include description if available (stored as a tag in MLflow)
            summary_lines.append(f"Description: {exp.tags['mlflow.note.content']}")
        # Fetch all runs for this experiment
        try:
            runs = self.client.search_runs([experiment_id], "", run_view_type="ACTIVE_ONLY", max_results=10000)
        except Exception as e:
            logger.error(f"Failed to search runs for experiment {experiment_id}: {e}")
            return []
        summary_lines.append(f"Total runs: {len(runs)}")
        # Create a document for experiment summary
        exp_metadata = {"source": "mlflow", "experiment_id": experiment_id, "type": "experiment"}
        docs.append(self._make_document("\n".join(summary_lines), exp_metadata))
        # Iterate through runs and summarize each
        for run in runs:
            run_id = run.info.run_id
            params = run.data.params
            metrics = run.data.metrics
            lines = [f"Run ID: {run_id}"]
            # List parameters
            if params:
                lines.append("Parameters:")
                for key, val in params.items():
                    lines.append(f"  - {key}: {val}")
            # List metrics
            if metrics:
                lines.append("Metrics:")
                for key, val in metrics.items():
                    lines.append(f"  - {key}: {val}")
            # Add run metadata (e.g., run name or status if needed)
            if run.info.status:
                lines.append(f"Status: {run.info.status}")
            content = "\n".join(lines)
            metadata = {"source": "mlflow", "experiment_id": experiment_id, "run_id": run_id, "type": "run"}
            docs.append(self._make_document(content, metadata))
        return docs
    
    def load_run(self, run_id: str):
        """
        Load a single MLflow run by ID, returning its parameters and metrics as a document.
        """
        try:
            run = self.client.get_run(run_id)
        except Exception as e:
            logger.error(f"Failed to get MLflow run {run_id}: {e}")
            return []
        params = run.data.params
        metrics = run.data.metrics
        lines = [f"Run ID: {run_id}"]
        if params:
            lines.append("Parameters:")
            for key, val in params.items():
                lines.append(f"  - {key}: {val}")
        if metrics:
            lines.append("Metrics:")
            for key, val in metrics.items():
                lines.append(f"  - {key}: {val}")
        content = "\n".join(lines)
        metadata = {"source": "mlflow", "run_id": run_id, "type": "run"}
        return [self._make_document(content, metadata)]
    
    def _make_document(self, text: str, metadata: dict):
        """Create a Document or dict for the MLflow metadata content."""
        try:
            from langchain.schema import Document
            return Document(page_content=text, metadata=metadata)
        except ImportError:
            return {"text": text, "metadata": metadata}
```

**Explanation:** This loader uses MLflow's Python API to retrieve experiment data. We initialize an `MlflowClient` with a given or default tracking URI (in a Databricks environment, using `'databricks'` as the URI will connect to the workspace's tracking server if credentials are configured). To get all runs of an experiment, we use `client.search_runs` with the experiment ID, which returns a list of Run objects containing metrics and parameters in `Run.data.metrics` and `Run.data.params`. The code compiles a summary of the experiment (including description and run count) and then iterates over each run to list its parameters and metrics. Each run's summary and the experiment summary are returned as separate documents, making it easy to search for specific runs by parameter or metric values. We also provide a `load_run` method for convenience, which fetches a single run by ID and formats its details similarly. Basic error handling is included to log issues such as missing experiments or failed MLflow queries.

## CSV File Loader

CSV files often contain datasets or tabular results. This loader uses **Pandas** to read CSV files and produce both a high-level summary and optional detailed documents for individual rows. The summary includes the number of rows and columns, the column names, and basic statistical descriptors for numeric columns (via `DataFrame.describe()` which gives a *“quick summary of key statistical metrics like mean, standard deviation, percentiles, and more”*). If configured to do so, the loader can also return each row of the CSV as a separate document (which can be useful for fine-grained search, but may be expensive for very large files).

```python
# File: loaders/csv_loader.py

import logging
import pandas as pd

logger = logging.getLogger(__name__)

class CSVLoader:
    """Loader for CSV files. Reads the file into a DataFrame and provides summary and optional row-level documents."""
    
    def __init__(self, include_rows: bool = False, max_rows: int = None):
        """
        Args:
            include_rows: If True, include each row of the CSV as an individual document.
            max_rows: Maximum number of row documents to include (None for no limit). Ignored if include_rows=False.
        """
        self.include_rows = include_rows
        self.max_rows = max_rows
    
    def load(self, path: str):
        """
        Load a CSV file and return a summary document and optionally row documents.
        
        Returns:
            List of Document (or dict) objects. The first document is a summary of the CSV. If include_rows is True,
            subsequent documents correspond to individual rows (up to max_rows).
        """
        try:
            df = pd.read_csv(path)
        except Exception as e:
            logger.error(f"Failed to read CSV {path}: {e}")
            return []
        docs = []
        # Summary document
        num_rows, num_cols = df.shape
        summary_lines = [
            f"CSV file: {path}",
            f"Rows: {num_rows}, Columns: {num_cols}",
            f"Columns: {', '.join(df.columns.astype(str))}"
        ]
        # If DataFrame has any numeric columns, include basic stats
        try:
            desc = df.describe(include='all', percentiles=[]).to_string()
            # Only include describe output if dataframe is not empty
            if num_rows > 0:
                summary_lines.append("Basic statistics:\n" + desc)
        except Exception as e:
            # describe might fail if no numeric or all non-numeric data; handle gracefully
            logger.warning(f"Could not generate describe() stats for {path}: {e}")
        summary_text = "\n".join(summary_lines)
        summary_metadata = {"source": path, "type": "csv_summary"}
        docs.append(self._make_document(summary_text, summary_metadata))
        # Optional individual row documents
        if self.include_rows:
            # Determine how many rows to document
            total = num_rows if self.max_rows is None else min(num_rows, self.max_rows)
            for i in range(total):
                row = df.iloc[i]
                # Represent the row as a series of "Column: Value"
                row_items = [f"{col}: {row[col]}" for col in df.columns]
                row_text = f"Row {i}: " + "; ".join(str(item) for item in row_items)
                row_metadata = {"source": path, "type": "csv_row", "row_index": i}
                docs.append(self._make_document(row_text, row_metadata))
        return docs
    
    def _make_document(self, text: str, metadata: dict):
        """Create a Document or dict for the CSV content."""
        try:
            from langchain.schema import Document
            return Document(page_content=text, metadata=metadata)
        except ImportError:
            return {"text": text, "metadata": metadata}
```

**Explanation:** The CSV loader uses `pandas.read_csv` to load the file into a DataFrame. We then build a summary string containing the file path, number of rows and columns, and the list of column names. We also attempt to append the output of `df.describe()` for a statistical overview – this provides counts, means, std deviation, min, max, etc., for numeric columns (and for non-numeric columns, `describe(include='all')` will give count and unique values, etc.). If the DataFrame is empty or all columns are non-numeric (causing `describe` to fail or be uninformative), we catch the exception and proceed without it.

If `include_rows` is enabled, the loader iterates over each row (up to `max_rows` if set) and creates a document where the content is a concatenation of "Column: Value" pairs for that row. Each row document gets metadata indicating its index. This can be useful to allow searching for specific row values in the documentation system. However, for large CSVs, including every row can be expensive, so the `max_rows` parameter can limit the number of per-row documents. All documents (the summary and each row) are returned in a list.

Basic logging is included to handle errors in reading the file or computing statistics. For example, if the CSV file is not found or is malformed, an error is logged and an empty list is returned (so the pipeline can continue without crashing).

## Image File Loader

Images (such as plots or diagrams saved as PNG/JPEG files) might be part of the project documentation. This loader does not attempt actual image content extraction (since that would require an OCR, which we treat as optional), but instead creates a placeholder textual description based on the image's metadata (filename and an inferred title). We strip the file extension and use the filename as a title (e.g., `"accuracy_plot.png"` becomes title `"Accuracy plot"`). This title is used as the document content so that the image can be indexed by its name or a simple description. If needed, this loader could be extended to perform OCR on the image to extract text, but here we keep it as a stub.

```python
# File: loaders/image_loader.py

import os
import logging

logger = logging.getLogger(__name__)

class ImageLoader:
    """Loader for image files. Generates a placeholder document with image metadata (filename as title)."""
    
    def __init__(self, use_ocr: bool = False):
        """
        Args:
            use_ocr: If True, (future) implement OCR to extract image text. Currently not used (placeholder only).
        """
        self.use_ocr = use_ocr
    
    def load(self, path: str):
        """
        Load an image file and return a document with a placeholder caption derived from the filename.
        
        Returns:
            List with one Document (or dict) containing the image title and metadata.
        """
        try:
            filename = os.path.basename(path)
            title = os.path.splitext(filename)[0]
            # Replace common separators with spaces and capitalize
            title_clean = title.replace("_", " ").replace("-", " ").strip().capitalize()
            if not title_clean:
                title_clean = "Untitled image"
            # Use the title as content (as a stand-in caption or description)
            content = f"Image: {title_clean}"
            metadata = {"source": path, "type": "image", "title": title_clean}
            return [self._make_document(content, metadata)]
        except Exception as e:
            logger.error(f"Failed to load image file {path}: {e}")
            return []
    
    def _make_document(self, text: str, metadata: dict):
        """Create a Document or dict for the image."""
        try:
            from langchain.schema import Document
            return Document(page_content=text, metadata=metadata)
        except ImportError:
            return {"text": text, "metadata": metadata}
```

**Explanation:** The image loader creates a dummy caption for the image using the file name. For example, an image file named `model_accuracy.png` will produce a document with content like `"Image: Model accuracy"` and metadata including the file path and a title "Model accuracy". This is a simplistic approach, but it ensures that images are not ignored in the documentation index—at minimum, one can search by the image name or a guess of its content from the title. We included a `use_ocr` flag in the initializer to suggest extensibility: if set to `True`, one could integrate an OCR library (e.g., Tesseract via `pytesseract`) to extract text from the image and include that in the content. In this placeholder implementation, we don't perform OCR; we only log an error if something goes wrong (like the file not being accessible). The loader returns a list with a single document for the image.

## Directory Structure Loader

For completeness, the directory loader generates a **tree representation** of the file/folder hierarchy of a given path. This can be useful to include an overview of the project structure in the documentation. We use Python's filesystem utilities to walk through the directory. The implementation below uses a recursive approach (with `os.listdir` or `Path.iterdir`) to build a tree string, but one could also use `os.walk` which *“generate\[s] the file names in a directory tree by walking the tree”*. The output is a single document containing a textual tree (with indents to show subdirectories).

```python
# File: loaders/directory_loader.py

import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DirectoryLoader:
    """Loader for directory structures. Produces a tree representation of all files and subdirectories."""
    
    def __init__(self, max_depth: int = None):
        """
        Args:
            max_depth: Optional maximum depth to traverse. None means no limit (full depth).
        """
        self.max_depth = max_depth
    
    def load(self, path: str):
        """
        Load the directory structure of the given path and return a document with the tree hierarchy.
        
        Returns:
            List with one Document (or dict) containing the directory tree as text.
        """
        path_obj = Path(path)
        if not path_obj.exists():
            logger.error(f"Directory path not found: {path}")
            return []
        if not path_obj.is_dir():
            logger.error(f"Path is not a directory: {path}")
            return []
        try:
            tree_lines = self._build_tree(path_obj, depth=0)
            tree_text = "\n".join(tree_lines)
            metadata = {"source": path, "type": "directory_tree"}
            return [self._make_document(tree_text, metadata)]
        except Exception as e:
            logger.error(f"Failed to build directory tree for {path}: {e}")
            return []
    
    def _build_tree(self, dir_path: Path, depth: int):
        """Recursively build the directory tree lines with indentation."""
        lines = []
        indent = "    " * depth
        # Include directory name with trailing slash
        lines.append(f"{indent}{dir_path.name}/")
        # Stop if max_depth is reached
        if self.max_depth is not None and depth >= self.max_depth:
            return lines
        # List children (files and dirs) sorted alphabetically
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: p.name.lower())
        except Exception as e:
            logger.warning(f"Cannot list directory {dir_path}: {e}")
            return lines
        for entry in entries:
            if entry.name.startswith('.'):
                continue  # skip hidden files/folders (optional behavior)
            if entry.is_dir():
                # Recurse into subdirectory
                lines.extend(self._build_tree(entry, depth + 1))
            else:
                lines.append(f"{'    ' * (depth + 1)}{entry.name}")
        return lines
    
    def _make_document(self, text: str, metadata: dict):
        """Create a Document or dict for the directory tree."""
        try:
            from langchain.schema import Document
            return Document(page_content=text, metadata=metadata)
        except ImportError:
            return {"text": text, "metadata": metadata}
```

**Explanation:** The directory loader walks through the given folder and its subfolders, constructing a textual tree. It starts at the root directory (whose name is included at depth 0) and recursively lists subdirectories and files. We indent sub-levels by four spaces for each depth level. By default, it will traverse the entire tree (no depth limit), but the `max_depth` parameter can be set to limit how deep it goes (e.g., `max_depth=1` would list only immediate children, `max_depth=2` includes grandchildren, etc.). Hidden files or directories (those starting with `.`) are skipped in this implementation for cleanliness.

We leveraged the filesystem APIs to gather directory contents. The approach is similar to using `os.walk`, which *“generate\[s] the file names in a directory tree by walking the tree either top-down or bottom-up”*. Here, we chose a recursive strategy for clarity, but either method is effective. The final output is a single string representing the tree, and we package that into a document. If the given path does not exist or is not a directory, we log an error and return an empty result. Any errors during traversal (for example, permission issues on certain subdirectories) are logged as warnings, and those branches are skipped.

Each loader above is designed to be modular and extensible. They include docstrings for clarity, use logging to aid debugging, and avoid hard-coding environment-specific details (like secrets or absolute paths). This modular design allows you to pick and choose which loaders to use for building a comprehensive documentation indexing system in a Databricks (or similar) ML project. Each loader returns content in a structured form that can be easily ingested by tools like LangChain or custom search indexes for downstream tasks like question-answering or full-text search over your project’s artifacts.
