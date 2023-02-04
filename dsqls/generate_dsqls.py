# Generate DSQL chunked by ids and grouped by file
#
# Script read file formatted with 1 id by line and generate DSQL
#
# Sample how to run this code
# python generate_dsqls.py -i resources/ids_from_db.txt -t "UPDATE tax_forms SET\n\t\`status\` = 'NOT_AVAILABLE'\nWHERE id IN ({});\n\n"
#
import sys
import getopt
import os
import codecs
import traceback
import math
import time
from itertools import (takewhile, repeat)


# Represents the extracted object from file's line
# Todo: refactory to represent the object required to build SQL Statement
class InputData:
    """ Represents the input data from file's line. Note Update this class to represent the file metadata"""

    def __init__(self, raw_data):
        # Represents the file row
        self.id: str = str(raw_data.rstrip())

    def __str__(self):
        return f'InputData( id: {self.id} )'

    def __repr__(self):
        return f'InputData( id: {self.id} )'


class DataChunk:
    """ Represents the data chunk of set"""

    def __init__(self, items: [InputData], max_chunk_size):
        self.items: [InputData] = items
        self.size: int = len(items)
        self.max_chunk_size: int = max_chunk_size

    def __str__(self):
        return f'DataChunk( size: {self.size}, max_chunk_size: {self.max_chunk_size} )'

    def __repr__(self):
        return f'DataChunk( size: {self.size}, max_chunk_size: {self.max_chunk_size} )'


class SQLCommand:
    """ Represents the SQL command"""

    def __init__(self, template, chunk: DataChunk):
        self.chunk: DataChunk = chunk
        # TODO: Replace with the required SQL command
        self.template: str = template

    """ Returns the number of rows will be affected"""

    def affected_items(self):
        return self.chunk.size

    """ Builds the SQL command. Note update this method to generate the required SQL output """

    def build_sql_statement(self):
        # TODO: Refactory this to build the expected SQL Result
        # e.id is property from InputData object
        combined_ids: str = ','.join(e.id for e in self.chunk.items)
        return self.template.format(combined_ids)

    def __str__(self):
        return f'SQLCommand( affected_items: {self.affected_items()})'

    def __repr__(self):
        return f'SQLCommand( affected_items: {self.affected_items()})'


# Represents DSQL file will be generated
class DSQLFile(object):
    """ Represents DSQL File """

    def __init__(self, id, sql_commands, max_chunk_size):
        self.id: int = id
        self.sql_commands: [SQLCommand] = sql_commands
        self.max_chunk_size: int = max_chunk_size

    """ Returns the number of entries will be affected """

    def total_affected_items(self):
        return sum(e.affected_items() for e in self.sql_commands)

    """ Returns the number of SQL commands available in the file """

    def total_sql_commands(self):
        return len(self.sql_commands)

    """ Builds the output file name """

    def build_output_file_name(self, output_path, output_file_name, total_files):
        return "{}/{}_{}_of_{}.sql".format(output_path, output_file_name, self.id, total_files)

    """ Builds the file header """

    def build_header(self, number_of_files):
        return "-- file: {} of {}, " \
               "affected_rows: {}, " \
               "max_chunk_size: {}, " \
               "total_sql_commands: {}\n\n".format(self.id,
                                                   number_of_files,
                                                   self.total_affected_items(),
                                                   self.max_chunk_size,
                                                   self.total_sql_commands())

    """ Builds the file content """

    def build_content(self):
        return '\n'.join(e.build_sql_statement() for e in self.sql_commands)

    def __repr__(self):
        # return f'DSQLFile( sql_commands: { len(self.sql_commands) })'
        return f'DSQLFile( id: {self.id}, ' \
               f'total_affected_items: {self.total_affected_items()}, ' \
               f'total_sql_commands: {self.total_sql_commands()} , ' \
               f'max_chunk_size: {self.max_chunk_size})'


class BuildDSQLFile(object):
    """ Loads entries (InputData) from the input file
        Returns list of InputData.
    """

    def load_input_entries(self, input_file_name):
        input_file = open(input_file_name, 'r')
        lines = input_file.readlines()
        entries = []

        for line in lines:
            entries.append(InputData(line))

        # close id file
        input_file.close()

        return entries

    """ Splits the entries in chunks
        Returns list of DataChunks
    """

    def split_entries(self, entries, max_chunk_size):
        result = []
        chunk = []

        for entry in entries:
            chunk.append(entry)

            if len(chunk) == max_chunk_size:
                result.append(DataChunk(chunk, max_chunk_size))
                # reset chunk
                chunk = []

        if len(chunk) > 0:
            result.append(DataChunk(chunk, max_chunk_size))

        return result

    """ Builds the SQL Statements
        Returns list of SQLCommand
    """

    def build_sql_commands(self, sql_template, chunks):
        sql_commands = []

        for data in chunks:
            sql_commands.append(SQLCommand(sql_template, data))

        return sql_commands

    """ Prepares the DSQL files representation.
        This method will populate the max SQL Commands support per file
        Returns list of DSQLFile
    """

    def build_dsql_files(self, init_file_id, sql_commands, max_sql_commands_per_file, max_chunk_size):
        dsql_files = []
        file_id = init_file_id
        group_sql_commands = []

        for sql_command in sql_commands:
            group_sql_commands.append(sql_command)

            if len(group_sql_commands) == max_sql_commands_per_file:
                dsql_files.append(DSQLFile(file_id, group_sql_commands, max_chunk_size))
                group_sql_commands = []
                file_id += 1

        if len(group_sql_commands) > 0:
            dsql_files.append(DSQLFile(file_id, group_sql_commands, max_chunk_size))

        return dsql_files

    """ Creates the DSQL Files
        Returns list of SQLCommand
    """

    def create_dsql_files(self, dsql_files, output_path, output_script_name):
        # Create DSQL files
        total_files = len(dsql_files)
        print(output_path)
        for dsql_file in dsql_files:
            self.create_dsql_file(dsql_file, output_path, output_script_name, total_files)

    def create_dsql_file(self, dsql_file, output_path, output_script_name, total_files):
        dsql_file_name = dsql_file.build_output_file_name(output_path, output_script_name, total_files)
        output_file = open(dsql_file_name, "a")
        output_file.write(dsql_file.build_header(total_files))
        output_file.write(dsql_file.build_content())
        output_file.close()

    def create_output_folder(self, output_path):
        isExist = os.path.exists(output_path)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(output_path)
            print("The new directory is created!")

    """ Process the input file by stream """

    def count_file_lines(self, filename):
        with open(filename, 'rb') as infile:
            buffer = takewhile(lambda x: x, (infile.raw.read(1024 * 1024) for _ in repeat(None)))
            return sum(buf.count(b'\n') for buf in buffer)

    def estimate_number_of_files(self, number_of_entries, chunk_size, sql_command_per_file):
        return int(math.ceil((number_of_entries / chunk_size) / sql_command_per_file))

    """ Process the input file by stream """

    def process_stream(self, input_file_name, output_path, output_script_name, sql_template, init_file_id, chunk_size,
                       sql_command_per_file):

        self.create_output_folder(output_path)
        number_of_entries = self.count_file_lines(input_file_name)
        estimate_number_of_files = self.estimate_number_of_files(number_of_entries, chunk_size, sql_command_per_file)

        with open(input_file_name) as infile:
            entries = []
            chunked_entries = []
            file_id = init_file_id

            for line in infile:
                entries.append(InputData(line))

                if len(entries) == chunk_size:
                    chunked_entries.append(DataChunk(entries, chunk_size))
                    entries = []

                if len(chunked_entries) == sql_command_per_file:
                    sql_commands = self.build_sql_commands(sql_template, chunked_entries)
                    dsql_file = DSQLFile(file_id, sql_commands, chunk_size)
                    self.create_dsql_file(dsql_file, output_path, output_script_name, estimate_number_of_files)
                    chunked_entries = []
                    file_id += 1

            if len(entries) > 0:
                chunked_entries.append(DataChunk(entries, chunk_size))
                sql_commands = self.build_sql_commands(sql_template, chunked_entries)
                dsql_file = DSQLFile(file_id, sql_commands, chunk_size)
                self.create_dsql_file(dsql_file, output_path, output_script_name, estimate_number_of_files)

            print("Number of files: %s ", file_id)
            print("Number of affected entries: %s ", number_of_entries)

    """ Process the input file, by loading all file in memory """

    def process(self, input_file_name, output_path, output_script_name, sql_template, init_file_id, chunk_size,
                sql_command_per_file):

        # load input entries (List of InputData)
        input_entries = self.load_input_entries(input_file_name)

        # split entries in chunks (List of DataChunk), this will be used to build SQL Statements
        chunked_entries = self.split_entries(input_entries, chunk_size)

        # build SQl commands
        sql_commands = self.build_sql_commands(sql_template, chunked_entries)

        # build DSQL files by grouping sql commands per file
        dsql_files = self.build_dsql_files(init_file_id, sql_commands, sql_command_per_file, chunk_size)

        self.create_output_folder(output_path)

        # create the output files
        self.create_dsql_files(dsql_files, output_path, output_script_name)


def process(argv):
    arg_help = "{0} -i <input file name>" \
               " -p <output path>" \
               " -o <output prefix script>" \
               " -c <chunk size>" \
               " -s <sql command by file>" \
               " -t <sql template.>" \
               " -f <file id init>".format(argv[0])

    # Number of ids by sql statement
    arg_chunk_size = 1000
    # Max number of sql instruction per a DSQL file.
    arg_sql_command_per_file = 10
    # init file id
    arg_init_file_id = 1
    # Target input file that contains the ids
    arg_input = 'resources/ids_from_db.txt'
    # Output path directory
    arg_output_path = 'output'
    # Output prefix filename
    arg_output_script_name = 'script'
    # The brackets will be replaced by the ids loaded from the file {}
    arg_sql_template = "UPDATE table_name SET\n\t`status` = 'NOT_AVAILABLE'\nWHERE id IN ({});\n\n"

    print(argv)
    try:
        opts, args = getopt.getopt(argv[1:], "h:i:c:s:f:o:t:p:", ["help", "input=",
                                                                  "chunk=", "sql=", "output_name=", "fileid=",
                                                                  "output_path=, template="])
    except Exception:
        print(arg_help)
        traceback.print_exc()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-i", "--input"):
            arg_input = arg
        elif opt in ("-c", "--chunk"):
            arg_chunk_size = int(arg)
        elif opt in ("-f", "--fileid"):
            arg_init_file_id = int(arg)
        elif opt in ("-t", "--template"):
            print(arg)
            arg_sql_template = codecs.decode(arg, "unicode_escape")
        elif opt in ("-p", "--path"):
            arg_output_path = arg
        elif opt in ("-o", "--output_name"):
            arg_output_script_name = arg
        elif opt in ("-s", "--sql"):
            arg_sql_command_per_file = int(arg)

    print('input file name (-i):', arg_input)
    print('init file id (-f):', arg_init_file_id)
    print('sql template (-t):', arg_sql_template)
    print('chunk size (-c):', arg_chunk_size)
    print('number of sql command by file (-s):', arg_sql_command_per_file)
    print('output path (-p):', arg_output_path)
    print('output prefix script name (-o):', arg_output_script_name)

    start_time = time.time()
    BuildDSQLFile().process_stream(arg_input, arg_output_path, arg_output_script_name, arg_sql_template,
                                   arg_init_file_id, arg_chunk_size, arg_sql_command_per_file)
    print("took %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    process(sys.argv)
