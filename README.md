### Needs a lot QoL but it works 
- OCR can get messy so it's definitely not 100% accurate
- Logs will be shown to check for incorrect names/dates and such
- Targetted for mobile since wish history gets harder to import now
- Just a 4fun side project that won't see much updates

To use, install python and run 
```
pip install -r requirements.txt
```

Run command below to start program, will automatically load from wish/ folder and save to wishes.json
```
python main.py
```
To change directories
```
python main.py -f wish_folder/ -json wishes.json
```
A list of help options
```
options:
  -h, --help            show this help message and exit
  -f [FOLDER_PATH], --folder_path [FOLDER_PATH]
                        folder path of all ss of wish history (sorted)
  -json [JSON_PATH], --json_path [JSON_PATH]
                        json path to store output result
  -src [SRC_EXCEL], --src_excel [SRC_EXCEL]
                        src excel (source excel file)
  -dst [DST_EXCEL], --dst_excel [DST_EXCEL]
                        dst excel (where modified excel file is saved)
  -d, --display         display
```
