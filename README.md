# pyutils-scripts
Some daily scripts to automate daily tasks


## Generate DSQL by chunk files

### Script
`create_chunked_dsqls_v3.py`


### Description

the Script will load input file where each line contains the id required to build the DSQLs.

### Arguments
  - `-i <input file name>`
  - `-c <chunk size>`
  -  `-s <sql command by file>`
  -  `-t <sql template.>`
  -  `-f <file id init>`
  -  `-o <output file name> `

Sample
``` bash
python create_chunked_dsqls_v3.py -o test -i ids2.txt -t "UPDATE test_table SET\n\t`status` = 'NOT_AVAILABLE'\nWHERE id IN ({});\n\n"

```

The ids2.txt file content:
```
550734
550735
550736
550737
550738
550739
550740
```
