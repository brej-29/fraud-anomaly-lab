# Kaggle API Setup

To download the **Credit Card Fraud Detection** dataset from Kaggle using the API, you must configure your Kaggle credentials.

## 1. Create a Kaggle Account and API Token

1. Go to https://www.kaggle.com/ and sign in (or create an account).
2. Click on your profile avatar → **Account**.
3. Scroll down to the **API** section.
4. Click **Create New API Token**.
5. A file named `kaggle.json` will be downloaded to your machine.

## 2. Place `kaggle.json` in the Correct Location

You have two main options:

### Option A: Default Location (`~/.kaggle`)

1. Create the directory if it does not exist:

   ```bash
   mkdir -p ~/.kaggle
   ```

2. Move the downloaded `kaggle.json` into this directory:

   ```bash
   mv ~/Downloads/kaggle.json ~/.kaggle/
   ```

3. Secure the file (recommended):

   ```bash
   chmod 600 ~/.kaggle/kaggle.json
   ```

The Kaggle API will automatically pick up credentials from this location.

### Option B: Custom Location (Using `KAGGLE_CONFIG_DIR`)

1. Choose a directory to store `kaggle.json`, e.g.:

   ```bash
   mkdir -p /path/to/kaggle-config
   mv ~/Downloads/kaggle.json /path/to/kaggle-config/
   ```

2. Set the `KAGGLE_CONFIG_DIR` environment variable to this directory, for example:

   ```bash
   export KAGGLE_CONFIG_DIR=/path/to/kaggle-config
   ```

3. You can add this `export` command to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) for persistence.

## 3. Install the Kaggle CLI

Install the Kaggle Python package (which includes the CLI):

```bash
pip install kaggle
```

Verify that it is available:

```bash
kaggle --version
```

## 4. Download the Dataset

Once configured, you can use:

- The shell script:

  ```bash
  ./scripts/download_kaggle.sh
  ```

- Or the Python helper:

  ```bash
  python -m ml.download_data
  ```

Both methods will download the dataset **Credit Card Fraud Detection** (`mlg-ulb/creditcardfraud`) into `data/raw/`.  
Raw data is **not** committed to git; it is for local use only.