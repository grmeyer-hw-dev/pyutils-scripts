# pyutils-scripts
Scripts to automate daily tasks


## Generate DSQL by chunk files
https://user-images.githubusercontent.com/107439697/216684789-4fd5e6a5-37f2-4a35-b188-a77c9f5eac3a.mp4

### Script
`generate_dsqls.py`

### Description

the Script will load input file where each line contains the id required to build the DSQLs.

### Arguments
  - `-i <input file name>` - (REQUIRED) the input file that contains the ids to generate the SQL commands
  -  `-t <sql template.>` - (REQUIRED) the SQL Command template. use `{}` to define where the ids will be replaced it.
  - `-o <output prefix script>` - rename output script prefix. By default is `output_<file index>_of_<total files>.sql`
  - `-p <output path>` - custom output path. by default is `output`
  - `-c <chunk size>` - chunk size each SQL command will process. e.g. 1000 entries
  -  `-s <sql command by file>` - Amount of SQL Commands by DSQL file. by default is 10 SQL Commands
  -  `-f <file id init>` - the init file index. by default is 1 but it's possible to start from 2 other number

#### Sample with required arg
Options:

``` bash
python generate_dsqls.py -i ids_from_db.txt -t "UPDATE test_table SET\n\t\`status\` = 'NOT_AVAILABLE'\nWHERE id IN ({});\n\n"
```

#### Sample with custom params
Options:

``` bash
python generate_dsqls.py -i ids2.txt -o custom_prefix -p "result/test1" -c 1000 -s 10 -t "UPDATE test_table SET\n\t\`status\` = 'NOT_AVAILABLE'\nWHERE id IN ({});\n\n"
```

#### The ids_from_db.txt file content:
```
550734
550735
550736
550737
550738
550739
550740
```

##### Test with sample resources
``` bash
python generate_dsqls.py -i resources/ids_from_db.txt -t "UPDATE test_table SET\n\t\`status\` = 'NOT_AVAILABLE'\nWHERE id IN ({});\n\n" -c 2 -s 3
```


#### Output:
![Screenshot 2023-02-02 at 3 46 20 PM](https://user-images.githubusercontent.com/107439697/216477024-192749e5-bb08-4a64-9bdf-6d4bfa18040f.png)

