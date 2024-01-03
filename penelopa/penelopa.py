_X='Chat completion: %s'
_W='max_tokens'
_V='temperature'
_U='The user task is: '
_T=' in terms to solve the user task: '
_S='%Y%m%d%H%M%S'
_R='Received invalid JSON response from GPT'
_Q='updated_code'
_P='original_code'
_O='file_path'
_N='answers'
_M='question'
_L='model'
_K='system'
_J=None
_I='listing'
_H='gpt_key'
_G='content'
_F='role'
_E=False
_D=True
_C='project'
_B='assistant_id'
_A='task'
import os,argparse,logging
from penelopa_dialog import PenelopaDialog
from codebaselister import CodebaseLister
from.configuration import ConfigManager
from datetime import datetime
import yaml,json
from.ai import AIClient
import re
def extract_json_from_text(text):
	try:
		match=re.search('```json(.+?)```',text,re.DOTALL)
		if match:json_str=match.group(1).strip();return json.loads(json_str)
		else:raise ValueError('No JSON found in text')
	except(ValueError,json.JSONDecodeError)as e:raise ValueError(f"Invalid or missing JSON data: {e}")from e
def apply_changes(file_path,changes):
	A='\n'
	with open(file_path,'r')as file:lines=file.readlines()
	line_offset=0
	for change in changes:
		line_num=change['line']+line_offset-1;new_lines=change['to'].split(A)
		if len(new_lines)>1:lines[line_num]=new_lines[0]+A;lines[line_num+1:line_num+1]=[line+A for line in new_lines[1:]];line_offset+=len(new_lines)-1
		else:lines[line_num]=new_lines[0]+A
	return lines
def confirm_changes(file_path,changes):
	print(f"Proposed changes for file: {file_path}")
	for change in changes:
		print(f"Change line {change['line']} from '{change['from']}' to '{change['to']}'");response=input('Confirm this change? (yes/no): ')
		if response.lower()not in['yes','y']:return _E
	return _D
class Penelopa:
	def __init__(self,config):self.config=config;self.api_client=AIClient(api_key=config[_H],model=config[_L])
	def save_config(self):
		try:
			with open(self.config['config_path'],'w')as file:yaml.safe_dump(self.config,file)
		except Exception as e:logging.error(f"Failed to save configuration: {e}")
	def run(self):
		if self.config['logging']:logging.basicConfig(level=logging.INFO)
		else:logging.basicConfig(level=logging.CRITICAL)
		logging.info('Running Penelopa');config=self.config.copy();config[_H]='*******';logging.info('Config: %s',config)
		if not self.config[_H]:self.obtain_gpt_key()
		if not self.config[_A]:self.obtain_task_description()
		updated_listing=_E
		if not self.config[_I]or not os.path.exists(self.config[_I])or updated_listing:updated_listing=self.obtain_listing()
		self.check_and_create_assistant(updated_listing);questions=self.obtain_clarifying_questions_for_task(self.config[_A]);dialog_responses=[]
		for(idx,question_data)in enumerate(questions,1):
			question_text=question_data[_M];answers=question_data[_N]
			while _D:
				print(f"\nQuestion {idx}: {question_text}")
				for(ans_idx,answer)in enumerate(answers,1):print(f" ({ans_idx}) {answer}")
				print('Please choose the number (1 to {}): '.format(len(answers)),end='');dialog=PenelopaDialog('');response=dialog.run()
				if response.isdigit()and 1<=int(response)<=len(answers):dialog_responses.append(int(response));break
				else:print('Invalid input. Please enter a number corresponding to the answer options.')
		logging.info('Clarifying questions generation completed');logging.info('answers: %s',dialog_responses);refined_task=self.refine_task_based_on_questions(self.config[_A],questions,dialog_responses);files=self.obtain_relevant_files(refined_task)
		for file_path in files['files']:
			if not os.path.isfile(file_path):logging.error(f"File {file_path} does not exist");continue
			with open(file_path,'r')as file:file_content=file.read()
			commands=self.request_code_update(file_path,file_content,refined_task);edit_blocks=self.parse_edit_blocks(commands);self.process_edit_blocks(edit_blocks)
	def parse_edit_blocks(self,response_text):
		edit_blocks=[];pattern=re.compile('```diff\\n(.*?)\\n<<<<<<< HEAD\\n(.*?)\\n=======\\n(.*?)\\n>>>>>>>',re.DOTALL);matches=pattern.findall(response_text)
		for match in matches:file_path,original_code,updated_code=match;edit_blocks.append({_O:file_path.strip(),_P:original_code.strip(),_Q:updated_code.strip()})
		logging.info('Edit blocks: %s',edit_blocks);return edit_blocks
	def process_edit_blocks(self,edit_blocks):
		for block in edit_blocks:
			file_path=block[_O];line_number=block.get('line_number');original_code=block[_P];updated_code=block[_Q];change_confirmed=self.confirm_change(file_path,original_code,updated_code)
			if change_confirmed:self.apply_change_to_file(file_path,original_code,updated_code,line_number)
	def confirm_change(self,file_path,original_code,updated_code):print(f"Proposed change for file: {file_path}");print('Original Code:\n'+original_code);print('Updated Code:\n'+updated_code);response=input('Apply this change? (1 for yes, 2 for no): ');return response.strip()=='1'
	def apply_change_to_file(self,file_path,original_code,updated_code,line_number=_J):
		MATCH_LENGTH=10
		with open(file_path,'r')as file:file_contents=file.readlines()
		if not file_contents or line_number is not _J:self.handle_new_code(file_contents,updated_code,line_number);updated=_D
		else:
			original_code_start=original_code[:MATCH_LENGTH];updated=_E
			for(idx,line)in enumerate(file_contents):
				if original_code_start in line:end_idx=idx+len(original_code.splitlines());file_contents[idx:end_idx]=updated_code.splitlines(keepends=_D);updated=_D;break
		if not updated:logging.error(f"Original code not found in {file_path}");return
		with open(file_path,'w')as file:file.writelines(file_contents)
		logging.info(f"Changes applied to {file_path}")
	def handle_new_code(self,file_contents,updated_code,line_number):
		if line_number is not _J:file_contents.insert(line_number-1,updated_code)
		else:file_contents.append(updated_code)
	def refine_task_based_on_questions(self,original_task,questions,user_responses):
		user_message="Refine the task description based on the user's answers to the clarifying questions. ";user_message+=f"Original task: {original_task}\n\n";user_message+='Details provided by the user based on clarifying questions:\n'
		for(question,response)in zip(questions,user_responses):user_message+=f" - For the question '{question[_M]}', the user selected: '{question[_N][response-1]}'\n"
		user_message+='\n Write only refined task in the response. The refined task should be about '+self.config[_C]+' itself only that you know (in file listing).';thread,run=self.api_client.create_thread_and_run(user_message,self.config[_B]);completed_run=self.api_client.wait_for_completion(thread.id,run.id);thread_messages=self.api_client.get_thread_messages(thread.id);refined_task=thread_messages[0].content[0].text.value;logging.info('Refined task: %s',refined_task);return refined_task
	def obtain_clarifying_questions_for_task(self,task_description):
		user_message=f'''
                Generate a set (3) of clarifying questions along with multiple choice answers for each question. The questions should help clarify the details and requirements of a given task. Ensure the output is in the specified JSON format. 
                Given the task description: "\'{self.config[_A]}\'" (and this task will be about the project \'{self.config[_C]}\' itself, that you know in the file listing), generate a list of clarifying questions along with options for possible answers. The response should be in JSON format, where each question is an object with "question" and "answers" fields.
                Example format:
                [
                    {{
                        "question": "What is the primary goal of the task?",
                        "answers": ["Optimizing performance", "Improving security", "Refactoring code"]
                    }}
                ]
                Answer only with json file with clarifying questions and answers.
                ''';thread,run=self.api_client.create_thread_and_run(user_message,self.config[_B]);completed_run=self.api_client.wait_for_completion(thread.id,run.id);thread_messages=self.api_client.get_thread_messages(thread.id);clarifying_questions_json=thread_messages[0].content[0].text.value
		try:clarifying_questions=extract_json_from_text(clarifying_questions_json)
		except json.JSONDecodeError:raise ValueError(_R)
		logging.info('Clarifying questions: %s',clarifying_questions);return clarifying_questions
	def request_code_update(self,file,file_content,refined_task):
		user_message=f"""
                        Given the task description: '{refined_task}' for project '{self.config[_C]}', generate a code update for the file '{file}': \"'{file_content}'\" (of the project '{self.config[_C]}' itself, that you know in the file listing). Provide a direct response in git-style edit block format. The response should detail the changes to be made to the file using git diff style blocks, including additions at specific line numbers if necessary.
                        Example formats:
                        ```diff
                        {file}
                        <<<<<<< HEAD
                        Line 10
                        =======
                            new code to be inserted at line 10
                        >>>>>>> updated
                        ```
                        CHANGES MUST START WITH ```diff AND END WITH ``` ONLY. 
                        AFTER ```diff MUST COME THE FULL FILE NAME WITH FULL PATH.
                        DO NOT PROVIDE PLACEHOLDERS IN THE RESPONSE. ONLY PROVIDE THE CHANGES TO BE MADE.
                        DO NOT COMMENT ON THE CODE. ONLY PROVIDE THE CHANGES TO BE MADE.
                        Ensure that the HEAD section is an exact set of sequential lines from the file. If specifying a line number for insertion, mention it clearly. Do not skip, elide, or omit any lines or whitespace. Provide precise and unambiguous changes.
                        """;thread,run=self.api_client.create_thread_and_run(user_message,self.config[_B]);valid_response_received=_E;attempt=0;max_attempts=10
		while not valid_response_received and attempt<max_attempts:
			attempt+=1;run=self.api_client.wait_for_completion(thread.id,run.id);response_text=self.api_client.get_thread_messages(thread.id)[0].content[0].text.value;logging.info('Response text: %s',response_text);code_block_count=response_text.count('```')
			if code_block_count>=2:valid_response_received=_D;logging.info(f"Edit blocks received and applied to {file}")
			else:logging.error('Response did not contain valid git-style edit blocks.')
		return response_text
	def obtain_relevant_files(self,refined_task):
		user_message=f'''
                Given the task description: "\'{refined_task}\'" for project "\'{self.config[_C]}\'" (that you know via file listing), generate a list of files that are relevant to the task that need to be updated. The response should be in JSON format, where each file is an object with the full file path.
                Example format:
                {{
                    "files": ["path/to/file1", "path/to/file2"]
                }}
                ''';thread,run=self.api_client.create_thread_and_run(user_message,self.config[_B]);completed_run=self.api_client.wait_for_completion(thread.id,run.id);thread_messages=self.api_client.get_thread_messages(thread.id);files_json=thread_messages[0].content[0].text.value
		try:files=extract_json_from_text(files_json)
		except json.JSONDecodeError:raise ValueError(_R)
		logging.info('files: %s',files);return files
	def check_and_create_assistant(self,updated_listing=_E):
		A='assistants'
		try:
			full_path_of_listing=os.path.abspath(self.config[_I])
			if not self.config[_B]:self.obtain_assistant_id(self.api_client.client);file=self.api_client.client.files.create(file=open(full_path_of_listing,'rb'),purpose=A);updated_listing=_E;self.api_client.client.beta.assistants.files.create(assistant_id=self.config[_B],file_id=file.id)
			if updated_listing:file=self.api_client.client.files.create(file=open(full_path_of_listing,'rb'),purpose=A);self.api_client.client.beta.assistants.files.create(assistant_id=self.config[_B],file_id=file.id)
		except Exception as e:logging.error(f"{e}")
	def obtain_listing(self):lister=CodebaseLister(output_filename='listing- '+datetime.now().strftime(_S)+'.txt');result=lister.generate_listing_file();logging.info(f"Listing file generated: {result}");output_filename=result['output_filename'];self.config[_I]=output_filename;self.save_config();return _D
	def obtain_assistant_id(self,client):
		logging.info('Obtaining assistant ID')
		if self.config[_B]:logging.info('Assistant ID already exists');return
		my_assistant=client.beta.assistants.create(instructions='You are a personal code exptert assistant about the project '+self.config[_C],name=self.config[_C]+' assistant-'+datetime.now().strftime(_S),tools=[{'type':'retrieval'}],model=self.config[_L]);self.config[_B]=my_assistant.id;self.save_config();return my_assistant
	def obtain_gpt_key(self):
		logging.info('Obtaining OpenAI GPT key')
		if self.config[_H]:logging.info('OpenAI GPT key already exists');return
		dialog=PenelopaDialog('Please enter your OpenAI GPT key: ');user_response=dialog.run();logging.info('User response: **********');self.config[_H]=user_response;self.save_config();return user_response
	def obtain_task_description(self):
		logging.info('Obtaining task description')
		if self.config[_A]:logging.info('Task description already exists');return
		dialog=PenelopaDialog('Please describe the task you need help with: ');user_response=dialog.run();logging.info('User response: %s',user_response);self.config[_A]=user_response;self.save_config();return user_response
	def obtain_files_to_analyze(self,client,project_structure):logging.info('Obtaining files to analyze');system_message='You are API that return files those need to be analyzed for the project '+self.config[_C]+_T+self.config[_A];user_messages=_U+self.config[_A]+'The structure of the project is: '+'\n '+project_structure+"\n Which file we need to analyze before solving a user task? Write the answer in the next json format: \n {'files': [\n   {'file_path': 'path/to/file'},\n ]}";chat_messages=[{_F:_K,_G:system_message}]+[{_F:'user',_G:user_messages}];chat_completion=client.chat.completions.create(messages=chat_messages,model=self.config['fine_tuned'],temperature=self.config[_V],max_tokens=self.config[_W],top_p=self.config['top_p']);response=chat_completion.choices[0].message.content.strip();logging.info(_X,response);chat_messages.append({_F:_K,_G:response});return chat_messages,response
	def obtain_commands_for_file(self,client,file,chat_messages):
		logging.info('Obtaining commands for file')
		if os.path.isfile(file):
			with open(file,'r')as f:file_content=f.read();system_message='You are API that return commands for file '+file+_T+self.config[_A];user_messages=_U+self.config[_A]+"The content of the file is: '"+file_content+"'\n Which commands we need to execute before solving a user task? Write the answer in the next json format: \n {'commands': [\n   {'line': number_of_line, 'new_line': 'new_line'},\n ]}";chat_messages.append({_F:_K,_G:system_message});chat_messages.append({_F:'user',_G:user_messages});chat_completion=client.chat.completions.create(messages=chat_messages,model=self.config[_L],temperature=self.config[_V],max_tokens=self.config[_W],top_p=self.config['top_p']);response=chat_completion.choices[0].message.content.strip();logging.info(_X,response);chat_messages.append({_F:_K,_G:response});return chat_messages
		else:return[]
def main():
	default_config_name='penelopa-config.yaml';parser=argparse.ArgumentParser(description='Penelopa: AI-driven codebase modifier')
	if os.path.exists(default_config_name):
		with open(default_config_name,'r')as file:default_config=yaml.safe_load(file)
	else:default_config=ConfigManager.DEFAULT_CONFIG
	parser.add_argument('--config_path',help='Path to the YAML configuration file for Penelopa. Defaults to "{}".'.format(default_config_name),default=default_config_name);parser.add_argument('--logging',help='Enable detailed logging output. Set to True for verbose logging.');parser.add_argument('--project',help='Name of the project Penelopa is working on. Used for task context.');parser.add_argument('--path',help='Path to the project directory that Penelopa will analyze and modify.');parser.add_argument('--task',help='Description of the task or problem Penelopa should assist with.');parser.add_argument('--gpt_key',help='API key for OpenAI GPT, necessary for communication with OpenAI services.');parser.add_argument('--model',help='Specifies the OpenAI GPT model to be used (e.g., "gpt-3.5-turbo").');parser.add_argument('--temperature',type=float,help='Sets the creativity level for the AI responses. Higher values generate more creative responses.');parser.add_argument('--top_p',type=float,help='Controls diversity of AI responses. Higher values allow for more diverse results.');parser.add_argument('--max_tokens',type=int,help='Maximum number of tokens (words) the AI can generate for each response.');parser.add_argument('--gitignore',action='store_true',help='Whether to consider .gitignore rules when analyzing the codebase.');parser.add_argument('--listing',help='Path to a file listing the contents of the project, used for contextual awareness.');parser.add_argument('--updated_listing',help='Indicate whether the listing file needs to be updated. Set to True to update.');parser.add_argument('--assistant_id',help='Unique identifier for the AI assistant instance used in this project.');args=parser.parse_args()
	if os.path.exists(default_config_name):
		with open(default_config_name,'r')as file:config=yaml.safe_load(file)
	else:config=ConfigManager.DEFAULT_CONFIG
	for(key,value)in vars(args).items():
		if value is not _J:config[key]=value
	penelopa_app=Penelopa(config);penelopa_app.run()
if __name__=='__main__':main()