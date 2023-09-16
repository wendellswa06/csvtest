import pandas as pd
import os
import time
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate, HumanMessagePromptTemplate
import sys
args = sys.argv

if len(args) < 1:
    print("Usage : py .py source_path template_path target_path")
    exit()
pathA = args[1]
pathT = args[2]
pathR = args[3]
# pathA = 'data/table_A.csv'
# # pathB = 'data/table_B.csv'
# pathT = 'data/template - Copy.csv'
# pathR = 'data/result.csv'


openai_api_key = '	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'
# openai_api_key = '	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'

chat_llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo-16k', openai_api_key=openai_api_key, verbose=False)

def get_column_names(path):
    df = pd.read_csv(path)
    column_names = df.columns.to_list()
    return column_names

def read_columns(path):
    column_list = []
    df = pd.read_csv(path)
    column_names = df.columns.to_list()
    
    for i in range(len(column_names)):
        head_content = f"{column_names[i]} : "
        content = df[column_names[i]].to_list()
        content = ",".join(map(str, content))
        head_content += f"{content}"
        # print(f"{head_content}\n")
        column_list.append(head_content)
    return column_list

contentA = read_columns(pathA)
# contentB = read_columns(pathB)
contentT = read_columns(pathT)

def find_similar(src_str, tgt_str):
    sys_template = (f"""You are a helpful assistant and you will be given one colmun from a table and a target table.
                    The column is formatted in this type : "column title : [elements separated by comma]"
                    The target table is formatted in this type : "column1|column2|...|columnN"
                    N is the number of columns in the table and column1, column2, ..., columnN are the columns in the table.
                    Each column(column1, column2, ..., columnN) of the table is formatted in the same type as the given column.
                    Your task is to find the most similar column in the target table for the given column based on analysis of the value, data type and the structure of the elements and the column titles of the given column and of the columns in the table and then return its title.
                    Here's the return style.
                    The most relavant column : column title
                                        
                    Here are two inputs.
                    The given column is {src_str}
                    The target table is {tgt_str}
                    """)
#                    They may differ in row names, value formats, value variants, are different samples from the same row or others.
                    #Print the zeroth value of the second row.
    system_message_prompt = SystemMessagePromptTemplate.from_template(sys_template)
    human_template = ""
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    result = chat_llm(chat_prompt.format_prompt(src_str=src_str, tgt_str=tgt_str).to_messages())
    print('---------------------------------------------------')
    # print(result.content.split('"')[3].split(':')[0].strip())
    return result


def generate_code(src_str, tgt_str):
    sys_template = ("""You are a helpful assistant and you will be given two columns from two tables.
                    Each column is formatted in this type : "[elements separated by comma]"
                    
                    Your task is to develop a function named convert_func which converts format of {src_str} into the format of {tgt_str} for general purpose.
                    {src_str} is the only one parameter which is passing through the convert_func.
                    Don't consider the number of elements in {src_str} and {tgt_str} or a specific number while displaying the result.
                    
                    Here is the return type.
                    output : convert_func
                    
                    Here are two columns to compare.
                    {src_str}
                    {tgt_str}
                    """)
    # i.e.
    #                 {src_str} = "name1 : [val1, val2,...]"
    #                 convert_func(val1), convert_func(val2) are possible but convert_func(src_str) is not possible.
#                    They may differ in row names, value formats, value variants, are different samples from the same row or others.
                    #Print the zeroth value of the second row.
    system_message_prompt = SystemMessagePromptTemplate.from_template(sys_template)
    human_template = ""
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    result = chat_llm(chat_prompt.format_prompt(src_str=src_str, tgt_str=tgt_str).to_messages())
    print('---------------------------------------------------')
    
    return result.content

def convert_table(source_path, template_path, target_path):

    src_path = "data/src.csv"
    temp_path = "data/temp.csv"
    if not os.path.exists(temp_path):
        f = open(temp_path, "w")
        f.close()
    if not os.path.exists(src_path):
        f = open(src_path, "w")
        f.close()
        
    df_source = pd.read_csv(source_path).dropna()
    
    
    df_template = pd.read_csv(template_path).dropna()
    df_template.to_csv(temp_path, index=False)
    # df_target = pd.read_csv(target_path)
    contentT = read_columns(temp_path)
    len_temp = df_template.shape[0]
    
    df_src = df_source[:len_temp]
    # print(list(df_src["FullName"]))
    # return {}, []
    df_src.to_csv(src_path, index=False)
    contentA = read_columns(src_path)
    # print(df_src)
    print('----------------------------------------------------------------')
    
    mapping_column = {}
    funcDict = {}
    tempNameList = list(df_template.columns)
    # print(tempNameList)
    for i in range(len(tempNameList)):
        relevantName = find_similar(contentT[i], contentA).content.split(':')[1].strip()
        mapping_column[tempNameList[i]] = relevantName
        time.sleep(i * 10)
    print(mapping_column)
    
    for idx, title in enumerate(mapping_column):
        col_nameA = mapping_column[title]
        colA = list(df_src[col_nameA])
        for i in range(len(colA)):
            colA[i] = str(colA[i])
        print(f"colA is {colA}")
        src_str = f"{col_nameA} : " + ",".join(colA)
        print(src_str)        
        tgt_str = contentT[idx]
        code1 = generate_code(src_str, tgt_str)
        time.sleep(10*(idx+1))
        # code2 = extract_code(code1)
        time.sleep(10*(idx+1))
        
        funcDict[col_nameA] = code1
    return mapping_column, funcDict

def filter_dataframe(source_path, mapper, fDict):
    
    df_src = pd.read_csv(source_path)
    tgt_filter = []
    col_filter = []
    new_name_list = []
    for idx, name in enumerate(mapper):
        # print(idx, name)
        col_filter.append(mapper[name])
        tgt_filter.append(name)
        new_name_list.append(name)
    
    df_filter = df_src[col_filter]
    return df_filter, new_name_list

columnMapper, funcDict = convert_table(pathA, pathT, pathR)
df_src, new_name_list = filter_dataframe(pathA, columnMapper, funcDict)
columnList = df_src.columns.to_list()
numCol = len(columnList)
try:
    
    for k in range(numCol):
        col = columnList[k]
        src_str = ','.join(map(str, df_src[col]))
        func = funcDict[col]
        exec(func)
        tgt_str = convert_func(src_str)
        df_src[col] = tgt_str.split(',')
        print(tgt_str)
except Exception as e:
    print("An error occurred while transforming: {e}")
df_src.columns = new_name_list
print(df_src)
if not os.path.exists(pathR):
    f = open(pathR, 'w')
    f.close()
df_src.to_csv(pathR, index=False)
os.remove("data/src.csv")
os.remove("data/temp.csv")
