To tailor the tutorial guide for your needs, could you please clarify the following:

1. What programming language will your dummy project use (e.g., Python, Scala, SQL)?
2. Are you targeting a specific Databricks runtime version or cluster configuration?
3. Would you like the tutorial to include Git integration and notebook handling within VS Code?
4. Should the tutorial assume you're using the Databricks Community Edition or an enterprise workspace?

Once I have this information, I can build a precise and useful step-by-step guide.

Great! I’ll put together a comprehensive tutorial guide that walks you through developing a Python project using the Databricks Extension for VS Code. It will include project setup, cluster integration, Git workflows, and tips for transitioning from notebooks to script-based development, all tailored for Databricks Runtime 16.3 and enterprise workspace users.

I’ll let you know once the guide is ready.

{
  "task_violates_safety_guidelines": false,
  "user_def_doesnt_want_research": false,
  "response": "Great! I’ll put together a comprehensive tutorial guide that walks you through developing a Python project using the Databricks Extension for VS Code. It will include project setup, cluster integration, Git workflows, and tips for transitioning from notebooks to script-based development, all tailored for Databricks Runtime 16.3 and enterprise workspace users.\n\nI’ll let you know once the guide is ready.",
  "title": "Databricks VS Code Extension Workflow for Python on Runtime 16.3",
  "prompt": "Create a comprehensive tutorial guide that walks through a complete development workflow using the Databricks Extension for Visual Studio Code, tailored for Python projects using Databricks Runtime 16.3 in an enterprise workspace. The guide should:\n\n- Introduce key features of the Databricks VS Code extension.\n- Show step-by-step project setup, including Git integration.\n- Demonstrate how to test and debug code using Databricks clusters from within VS Code.\n- Provide a dummy Python project as a hands-on example.\n- Include best practices for efficient development.\n- Include additional tips, workflows, or lesser-known but useful features.\n- Emphasize moving away from notebooks to a script-based workflow.\n\nFormat the response as a well-organized tutorial document with clear headings, and provide code snippets or configuration files where necessary."
}

# Developing Python Projects with the Databricks VS Code Extension (Runtime 16.3)

This tutorial walks through a full Python development workflow using the **Databricks Extension for Visual Studio Code**, targeting Databricks Runtime 16.3. You will learn how to set up a project, integrate Git, run and debug code on Databricks clusters, and apply best practices. We use a simple “dummy” Python example to demonstrate each step. The focus is on a **script-based workflow** (using `.py` files) rather than editing notebooks in the UI.

## Key Features of the Databricks VS Code Extension

The Databricks VS Code extension connects your local IDE to remote Databricks workspaces. Key capabilities include:  

- **Run and Debug Code** – Run local Python scripts on remote Databricks clusters or serverless compute with one click. You can also run files (or notebooks) as scheduled jobs in the workspace [What is the Databricks extension for Visual Studio Code? | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/#:~:text=The%20Databricks%20extension%20for%20Visual,You%20can%20then).  
- **Databricks Connect Integration** – Debug Python code locally while executing Spark operations on a remote cluster via Databricks Connect. Breakpoints, variable watches, and step-by-step debugging work in VS Code [What is the Databricks extension for Visual Studio Code? | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/#:~:text=The%20Databricks%20extension%20for%20Visual,You%20can%20then) [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug).  
- **One-way Code Sync** – Automatically upload your local project files to a designated workspace folder or Git repository in Databricks. (The extension keeps a one-way sync from local to workspace; do not edit synced files directly in Databricks [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python) [Using Git folders with Databricks extension for Visual Studio Code - Azure Databricks | Azure Docs](https://docs.azure.cn/en-us/databricks/archive/dev-tools/vscode-repos#:~:text=The%20Databricks%20extension%20for%20Visual,but%20is%20no%20longer%20recommended).)  
- **Asset Bundles / CI-CD Support** – Define jobs, pipelines and configuration in YAML (`databricks.yml`) and use the extension’s Asset Bundle UI to deploy them. You can create, deploy, and view bundles from VS Code [What is the Databricks extension for Visual Studio Code? | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/#:~:text=The%20Databricks%20extension%20for%20Visual,You%20can%20then) [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python).  
- **Git and Repo Integration** – Maintain your code in Git and optionally sync with Databricks Repos. (Databricks generally recommends using workspace folders over legacy Git folders [Using Git folders with Databricks extension for Visual Studio Code - Azure Databricks | Azure Docs](https://docs.azure.cn/en-us/databricks/archive/dev-tools/vscode-repos#:~:text=The%20Databricks%20extension%20for%20Visual,but%20is%20no%20longer%20recommended).) The extension can create and sync to a repo in your workspace and adds the `.databricks/` config folder to `.gitignore` [Set up authorization for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/authentication#:~:text=The%20extension%20creates%20a%20folder,extension%20for%20Visual%20Studio%20Code).  

<img src="https://docs.databricks.com/_images/vscode-extension.png" alt="Databricks VS Code Extension UI" width="600"/>  

These features make VS Code a full-fledged Databricks IDE. You can develop in a familiar editor, manage code via Git, and leverage the power of Databricks clusters without switching contexts [What is the Databricks extension for Visual Studio Code? | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/#:~:text=The%20Databricks%20extension%20for%20Visual,You%20can%20then) [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug).

## Prerequisites

- **Install the extension.** In VS Code, go to Extensions (`⇧⌘X`), search for “Databricks”, and install **Databricks VSCode**.  
- **Databricks access.** You need a Databricks workspace (Azure or AWS) with Databricks Runtime 16.3 available. Ensure you have a running cluster (or permissions to create one) and a personal access token (PAT) or OAuth login for authentication. Databricks Connect (if used) requires Unity Catalog enabled on the workspace [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug).  
- **Local Python environment.** Install Python 3.12 (the same major version as the remote runtime). Databricks Runtime 16.3 uses Python **3.12.3** [Databricks Runtime 16.3 - Azure Databricks | Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/release-notes/runtime/16.3#:~:text=distribution.%20%2A%20Java%3A%20Zulu17.54%2B21,Delta%20Lake%3A%203.3.0), so create a matching virtualenv or Conda environment. Use a tool like `venv` or `conda` to manage dependencies locally.  

## Step 1: Create a New Databricks Project

1. **Open or create a local folder.** In VS Code, go to **File > Open Folder** and select an (empty) directory for your project.  
2. **Launch the extension.** Click the Databricks icon in the VS Code sidebar. This opens the Databricks Extension panel [What is the Databricks extension for Visual Studio Code? | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/#:~:text=The%20Databricks%20extension%20for%20Visual,You%20can%20then).  
3. **Create a Databricks project.** In the Extension panel, click **Create a new project** (or **Create configuration**) and select your Databricks host URL. For example: `https://dbc-<instance>.cloud.databricks.com`.  
4. **Authenticate.** When prompted, choose **OAuth** or **Personal Access Token** authentication. Follow the on-screen steps to sign in or paste your token [Set up authorization for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/authentication#:~:text=The%20extension%20creates%20a%20folder,extension%20for%20Visual%20Studio%20Code). The extension will create a `.databricks/` folder in your project with a `databricks.env` file to store the workspace host and profile [Set up authorization for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/authentication#:~:text=The%20extension%20creates%20a%20folder,extension%20for%20Visual%20Studio%20Code). (VS Code also adds `.databricks/` to `.gitignore` so you don’t commit these secrets.)  
5. **Configure defaults.** You can accept defaults for workspace folder (used for code sync) and Bundle configuration if prompted. For a simple script-based workflow, you don’t need any sample notebooks or pipelines.  

At this point you have a Databricks project configured in VS Code. You can view or edit the `databricks.yml` and `databricks.env` under the `.databricks/` folder if needed (they store the workspace host, etc.). The extension’s **Configuration** pane is now active for this project.

## Step 2: Select or Create a Cluster

The extension needs a Databricks cluster (or serverless compute) to run your code. In the Databricks panel:

1. **Click the Configure Cluster icon.** In the Configuration view under “Cluster”, click the gear (⚙) icon [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python) [Configure your Databricks project using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/configure#workspace-folder#:~:text=Databricks%20recommends%20that%20you%20create,immediately%2C%20minimizing%20compute%20management%20overhead).  
2. **Choose a cluster.** In the Command Palette, select an existing cluster from your workspace, or choose **Create New Cluster** to spin up a new one [Configure your Databricks project using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/configure#workspace-folder#:~:text=Databricks%20recommends%20that%20you%20create,immediately%2C%20minimizing%20compute%20management%20overhead). (If you create a new cluster, VS Code will open the Databricks web UI to define it; after creating it, click back to VS Code and re-run the **Configure Cluster** command to attach it [Configure your Databricks project using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/configure#workspace-folder#:~:text=Databricks%20recommends%20that%20you%20create,immediately%2C%20minimizing%20compute%20management%20overhead) [Configure your Databricks project using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/configure#workspace-folder#:~:text=Databricks%20recommends%20that%20you%20create,immediately%2C%20minimizing%20compute%20management%20overhead).)  
3. **Start the cluster.** Once a cluster is selected, click the *play* icon (▶) next to its name in the Databricks pane. This starts the cluster if it is not already running [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python). You can also stop or restart clusters from this pane. The selected cluster’s ID and Runtime (16.3) will be displayed in the configuration view [Configure your Databricks project using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/configure#workspace-folder#:~:text=Databricks%20recommends%20that%20you%20create,immediately%2C%20minimizing%20compute%20management%20overhead).

Once attached, the extension will use this cluster for running code and jobs. (Tip: use a **Personal Compute** cluster for development, as recommended [Configure your Databricks project using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/configure#workspace-folder#:~:text=Databricks%20recommends%20that%20you%20create,immediately%2C%20minimizing%20compute%20management%20overhead).)

## Step 3: Enable Databricks Connect (for Debugging)

To debug code locally with Spark operations on the remote cluster, enable Databricks Connect:

1. **Activate your Python env.** In the Configuration pane under *Python Environment*, click **Activate Virtual Environment**. Select your `venv` or Conda environment that matches Python 3.12 [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug).  
2. **Install Databricks Connect.** In the same pane, click **Install databricks-connect**. The extension checks your cluster compatibility. If needed, attach a Unity Catalog-enabled cluster (Connect v2 requires UC) [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug) [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug). Follow prompts to install the `databricks-connect` package into your environment [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug) [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug).  
3. **Enable Connect.** If the Databricks Connect button is red, click it and follow instructions to finalize setup. Once enabled, the button turns green. You are now ready to use Databricks Connect for debugging [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug).

Note: Databricks Connect for Runtime 16.3 requires version 13.x of the client (matching Scala 2.12 Spark 3.5.2). The extension will install the correct version for you, or you can pin it manually (e.g. `poetry add databricks-connect==13.3.2` to match the one installed by the extension [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug)).

## Step 4: Create a Dummy Python Project

Let’s create a simple example to illustrate the workflow. In your project folder:

1. **Add a Python script.** Create a file `demo.py` in the project root. For example:

   ```python
   # demo.py – create a Spark DataFrame and show some data
   from pyspark.sql import SparkSession
   from pyspark.sql.types import *

   spark = SparkSession.builder.getOrCreate()

   schema = StructType([
       StructField("CustomerID", IntegerType(), False),
       StructField("FirstName",  StringType(),  False),
       StructField("LastName",   StringType(),  False)
   ])

   data = [
      [1000, 'Alice',  'Smith'],
      [1001, 'Bob',    'Jones'],
      [1002, 'Charlie','Brown']
   ]

   customers = spark.createDataFrame(data, schema)
   customers.show()
   ```

   This code uses PySpark to create a small DataFrame and display it. You can adapt it or add more logic (joins, filters, writes, etc.) as needed. The above snippet is similar to official examples [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python).

2. **Configure dependencies (optional).** If your script needs extra libraries (e.g. Pandas, NumPy, custom packages), install them in your local env. To ensure the cluster has the same libraries, you can add them as cluster libraries via the Databricks UI (or `%pip install` in code), or use the Asset Bundles config to specify libraries. For this simple example, no extra packages are needed beyond Spark.

3. **Initialize Git and push.** (Optional but recommended) Use Git to version your project. In the VS Code terminal, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Databricks VSCode demo"
   ```
   Connect to your remote Git repository (e.g. GitHub) and push. Databricks lets you link your workspace to Git, but our workflow assumes code is managed externally and deployed via jobs or CI/CD.

4. **(Optional) Set up a Databricks Repos folder.** If you want your code synced in the Databricks workspace for collaboration, consider using **Databricks Repos** (Workspace → Repos UI). Alternatively, the extension can sync to a workspace directory (see Sync below). For Git-based CI/CD, Databricks recommends using *workspace files* (Asset Bundles) over the older Git folders [Using Git folders with Databricks extension for Visual Studio Code - Azure Databricks | Azure Docs](https://docs.azure.cn/en-us/databricks/archive/dev-tools/vscode-repos#:~:text=The%20Databricks%20extension%20for%20Visual,but%20is%20no%20longer%20recommended).

## Step 5: Running Code on the Cluster

With the cluster running and your code ready, you can execute `demo.py` on Databricks:

- **Run on Databricks (interactive).** In the `demo.py` editor tab, click the Databricks icon ▶ next to the tab title. Choose **Run on Databricks > Upload and Run File** [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python). The extension uploads `demo.py` to a temporary workspace folder and executes it on the attached cluster. The Spark output appears in the **Debug Console** (View > Debug Console).

- **Alternative (context menu).** You can also right-click the file in the Explorer, select **Run on Databricks > Upload and Run File**. Both methods yield the same result.

   For our example, you should see the DataFrame printed:
   ```
   +----------+---------+--------+
   |CustomerID|FirstName|LastName|
   +----------+---------+--------+
   |      1000|    Alice|   Smith|
   |      1001|      Bob|   Jones|
   |      1002|  Charlie|   Brown|
   +----------+---------+--------+
   ```

- **Run as Job.** To run the code as a one-time or scheduled job, use **Run on Databricks > Run File as Workflow** [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python). This submits the file as a job run in your workspace (Databricks Lakehouse Jobs). The output will open in a new editor tab. You can also right-click the file and select **Run as Workflow**. (Behind the scenes, this creates a one-time job run using your file as the job’s task.)

## Step 6: Debugging with Databricks Connect

To debug `demo.py` interactively:

1. **Set breakpoints.** In `demo.py`, click in the left gutter to add breakpoints (e.g. inside the code after creating the DataFrame).  
2. **Debug with Connect.** Click the run icon ▶ and choose **Debug current file with Databricks Connect** [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug). Alternatively, right-click `demo.py` and pick **Run on Databricks > Debug current file with Databricks Connect**.

   The code will execute locally in VS Code (so you can step through it) while Spark computations run on the remote cluster. Variable states, stack traces, and console logs appear in the **Debug Console** and **Debug pane**. For example, you can inspect `customers` after it is created.

Databricks Connect uses the cluster’s Spark engine but runs your driver code locally. Remember to use a matching Python version and install all necessary libraries in your local environment. See the official guide for more details on notebook cell debugging (which uses similar mechanics) [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python) [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug).

## Step 7: Writing and Running Tests

Instead of manually inspecting results, you can write automated tests for your Spark code:

1. **Add a test file.** For example, create `test_demo.py`:
   ```python
   # test_demo.py – unit tests for demo.py
   from pyspark.sql import SparkSession
   import pytest

   @pytest.fixture
   def spark():
       # Create or get SparkSession on cluster
       return SparkSession.builder.getOrCreate()

   def test_customer_count(spark):
       data = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
       df = spark.createDataFrame(data, schema=["id", "name"])
       assert df.count() == 3
   ```
   This simple test checks the row count. Use PySpark and `pytest` idioms (names starting with `test_`). The `spark` fixture provides the cluster’s `SparkSession` to the test.  

2. **Install pytest on the cluster.** Before running tests on the cluster, ensure `pytest` is installed there. In the Databricks workspace UI, go to your cluster’s Libraries tab. If `pytest` is not listed, click *Install New* → *PyPI* and enter `pytest` [Run tests with pytest using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/pytest#:~:text=Make%20sure%20that%20,Databricks%20workspace%2C%20do%20the%20following). Wait for it to install.

3. **Create a test runner script.** In VS Code, add a runner file `pytest_databricks.py` in the project root:
   ```python
   import pytest, os, sys

   # Change to project root in workspace
   dir_root = os.path.dirname(os.path.realpath(__file__))
   os.chdir(dir_root)
   sys.dont_write_bytecode = True

   # Run pytest on all tests in this directory
   retcode = pytest.main(sys.argv[1:])
   ```
   This script invokes pytest in the cluster environment.

4. **Configure VS Code launch.** Create or edit `.vscode/launch.json` to add a Databricks run configuration. For example:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "type": "databricks",
         "request": "launch",
         "name": "Unit Tests (on Databricks)",
         "program": "${workspaceFolder}/pytest_databricks.py",
         "args": ["."],
         "env": {}
       }
     ]
   }
   ```
   This tells VS Code to run our test runner on the cluster [Run tests with pytest using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/pytest#:~:text=Make%20sure%20that%20,Databricks%20workspace%2C%20do%20the%20following).

5. **Run the tests.** In VS Code, open the Run/Debug pane and select **Unit Tests (on Databricks)**. Click the green ▶ button to start. The extension will sync your code and run the tests on the cluster. Test results appear in the Debug Console [Run tests with pytest using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/pytest#:~:text=Make%20sure%20that%20,Databricks%20workspace%2C%20do%20the%20following). For example:
   ```
   ... collected 1 item
   test_demo.py .                                                 [100%]
   ================== 1 passed in 2.34s ================================
   ```
   (A dot `.` means a test passed; `F` would indicate failure.)

This demonstrates how you can fully test Spark code on your remote cluster from VS Code. The same pattern works for any pytest tests. The Databricks extension automates the setup: syncing code, launching the cluster session, and showing the output.

## Best Practices and Tips

- **Version Control:** Keep your code in a Git repository (GitHub, GitLab, Azure Repos, etc.) and develop in feature branches. Use Databricks Repos or Asset Bundles for production deployments. Databricks recommends separate “user” and “production” Git folders in the workspace for collaborative workflows [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python).  
- **Environment Consistency:** Align your local Python environment with the cluster’s. Databricks Runtime 16.3 uses Python 3.12.3 [Databricks Runtime 16.3 - Azure Databricks | Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/release-notes/runtime/16.3#:~:text=distribution.%20%2A%20Java%3A%20Zulu17.54%2B21,Delta%20Lake%3A%203.3.0), so use Python 3.12 locally. Use virtualenv or Conda to manage dependencies. Avoid version mismatches between local packages and cluster libraries.  
- **Cluster Libraries:** Install necessary libraries on the cluster (via UI or `%pip`) to match your code’s requirements. For example, if using Pandas or other packages, add them as libraries to the cluster or use `%pip install` in the code.  
- **Databricks Connect:** Remember that Databricks Connect requires Unity Catalog and matching cluster Python version. After enabling Connect, use breakpoints and run/debug as usual. For production runs, you can *disable* Connect (the code will simply upload/run).  
- **Notebook Magics:** If you do use notebooks, you can debug `.py` notebooks (Jupyter format) or `.ipynb` notebooks in VS Code [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python) [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python). However, for a clean CI/CD pipeline, prefer pure `.py` scripts.  
- **Asset Bundles:** If your project will include complex jobs or DLT pipelines, use the Databricks Asset Bundles format (`databricks.yml`) to define them as code. The extension’s *Bundle Explorer* lets you manage jobs, pipelines, and variables in VS Code [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python).  
- **One-way Sync Warning:** The extension sync to workspace is one-way. Do **not** edit synced files in Databricks UI, as those changes will not come back to your local project [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python). Always make changes locally and re-run to sync.  
- **`.databricks` Folder:** The extension creates a `.databricks/` config folder with `databricks.env` and possibly `databricks.yml`. This folder is automatically added to `.gitignore` [Set up authorization for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/authentication#:~:text=The%20extension%20creates%20a%20folder,extension%20for%20Visual%20Studio%20Code) so it won’t be committed. Keep its contents (workspace, tokens) secure.  
- **Use Cluster Policies:** In enterprise workspaces, cluster policies and tags may be enforced. Tag your dev clusters (e.g. “dev”) and keep them running for short tasks. Configure cluster lifetimes to save cost.  
- **Debug Console & Logs:** All execution output (print statements, Spark output, pytest results) goes to the VS Code Debug Console. You can also inspect logs in Databricks (UI) for failed runs.  
- **PySpark UDFs and `%pip`:** The extension supports many notebook magics (like `%fs`, `%sql`, `%pip`) when debugging with Connect [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python). This is useful for installing packages on the fly in the remote session.  
- **Testing Non-Spark Code Locally:** You can run `pytest` locally for any pure-Python logic that doesn’t need Spark. Reserve the Databricks cluster for Spark-dependent tests.  

By following these practices—script-based development, version control, environment alignment, and automated testing—you ensure a robust workflow. You reduce reliance on fragile notebooks and make your code easier to review and maintain.

## Additional Tips

- **Multiple Databricks Projects:** You can have multiple Databricks projects open in one VS Code workspace and switch between them (in the Databricks pane, click “Local Folder” to select the active project) [What is the Databricks extension for Visual Studio Code? | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/#:~:text=The%20Databricks%20extension%20for%20Visual,You%20can%20then). This is handy if you work on several bundles or repos.  
- **Databricks CLI in Terminal:** You can also use the `databricks-cli` in the VS Code terminal (with your credentials set up) to perform tasks like uploading files to DBFS, listing jobs, etc., alongside the extension’s UI.  
- **Use Databricks SDK:** The Databricks SDK for Python (`databricks-sdk`) is preinstalled in Runtime 16.3 [Databricks Runtime 16.3 - Azure Databricks | Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/release-notes/runtime/16.3#:~:text=distribution.%20%2A%20Java%3A%20Zulu17.54%2B21,Delta%20Lake%3A%203.3.0). You can write scripts that call Databricks REST APIs via the SDK directly from VS Code (e.g. for advanced automation).  
- **Live Preview (Experimental):** Some VS Code features like “Databricks View” for notebooks or a data viewer for Spark DataFrames may be available as previews in the extension. Check the extension’s release notes for new features.  
- **Keep VS Code & Extension Updated:** The Databricks VS Code extension receives regular updates. Newer versions may introduce features (e.g. improved notebooks support, repo sync) and bug fixes. Use the latest extension and refer to Databricks docs for any version-specific notes (as of 2025, we’re focusing on version 2.x features).  

## Summary

Using the Databricks VS Code extension, you can fully develop Python data engineering or analytics code in VS Code on Databricks Runtime 16.3. You set up a project, connect your workspace and cluster, then write `.py` scripts instead of notebooks. Run code on the cluster with a click, debug with Databricks Connect, and even write full unit tests that run on the cluster. By keeping code in Git and using scripts, you gain reproducibility, code review, and CI/CD friendliness. This guide has walked through each step of that workflow with example commands and code.  

**Sources:** Official Databricks documentation for the VS Code extension features and tutorials [What is the Databricks extension for Visual Studio Code? | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/#:~:text=The%20Databricks%20extension%20for%20Visual,You%20can%20then) [Tutorial: Run Python on a cluster and as a job using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/tutorial#:~:text=Python) [Debug code using Databricks Connect for the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect#:~:text=1,want%20to%20run%20or%20debug) [Run tests with pytest using the Databricks extension for Visual Studio Code | Databricks Documentation](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/pytest#:~:text=Make%20sure%20that%20,Databricks%20workspace%2C%20do%20the%20following), and Databricks Runtime 16.3 release notes [Databricks Runtime 16.3 - Azure Databricks | Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/release-notes/runtime/16.3#:~:text=distribution.%20%2A%20Java%3A%20Zulu17.54%2B21,Delta%20Lake%3A%203.3.0). These sources provide details on the extension’s capabilities and the cluster environment used in this example.  



Great question! Here’s how **local project files** relate to files in your **Databricks workspace** when using the Databricks VS Code extension:

---

### 1. **Are local files automatically synced to Databricks workspace?**

- **Yes, but only one-way, on demand.**  
  When you use commands like **Run on Databricks** or **Upload**, the extension **uploads your local files** (scripts, config, etc.) **to a specific folder in the Databricks workspace**, usually under a temp or configured workspace path.

- **But it is a one-way sync:**  
  - Changes you make **locally** can be pushed to Databricks workspace.  
  - Changes made **directly in Databricks workspace UI** (like editing a notebook or script there) **do NOT sync back to your local project**.

---

### 2. **Where are the files uploaded in Databricks workspace?**

- By default, the extension uploads to a folder in the workspace under a path like:  
  ```
  /Users/<your-email-or-username>/vscode-sync/
  ```  
- You can configure or check the workspace folder path in the extension settings or in `.databricks/databricks.yml` (if using Asset Bundles or config files) .

- You can view these files via the **Databricks Workspace UI → Workspace → Users → <your username> → vscode-sync** folder.

---

### 3. **How to keep local and workspace files in sync?**

- **Best practice:**  
  - Always **edit your files locally** in VS Code.  
  - Use the extension’s commands (**Run**, **Upload**) to push changes to the workspace before running or debugging.  
  - **Do not edit synced files directly in the Databricks UI**, as local changes will overwrite workspace changes on next upload.  

- **Git integration is recommended:**  
  - Keep your source code versioned in Git and deploy from your local machine or CI/CD pipeline to Databricks.  
  - Databricks Repos can sync a Git repo inside the workspace, but the VS Code extension **does not automatically sync your local folder with Databricks Repos**; those are two separate sync mechanisms .

---

### 4. **Summary**

| Aspect                      | Details                                                          |
|-----------------------------|-----------------------------------------------------------------|
| Sync direction              | One-way: Local → Databricks workspace (on command)              |
| Default upload folder       | `/Users/<username>/vscode-sync/`                                |
| Workspace edits             | **Not synced back** to local files                               |
| Recommended workflow        | Edit locally → upload/run via extension → view results in workspace |
| Git integration             | Use for version control and CI/CD deployment                    |
| Databricks Repos            | Separate workspace Git integration, not auto-synced by VS Code |

---

If you want **two-way sync with notebooks or scripts**, consider using **Databricks Repos** in the workspace with Git integration, then edit in VS Code using the Repos clone feature (which syncs with workspace Git). But for script-based projects managed purely locally, use the VS Code extension upload/run commands and treat the workspace as a runtime/execution environment rather than a source repo.

---

**Let me know if you want a detailed walkthrough on configuring workspace folders or using Databricks Repos for better sync!**