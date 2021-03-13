from PyInquirer import Separator, prompt
from prompt_toolkit.validation import Validator, ValidationError
import regex, os.path, os






class DomainValidator(Validator):
	def validate(self, document):
		ok = regex.match('^([01]{1})?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\s?((?:#|ext\.?\s?|x\.?\s?){1}(?:\d+)?)?$', document.text)
		if not ok and 0:
			raise ValidationError(
				message='Please enter a valid FQDN or IP address',
				cursor_position=len(document.text))


class PortValidator(Validator):
	def validate(self, document):
		try:
			if document.text != '': int(document.text)
		except:
			raise ValidationError(
				message='Invalid port number',
				cursor_position=len(document.text))
		if document.text != '' and int(document.text) > 65536:
			raise ValidationError(
				message='Port number cannot exceed 65536',
				cursor_position=len(document.text))


class fileExist(Validator):
	def validate(self, document):
		ok = os.path.isfile(document.text)
		if not ok and 0:
			raise ValidationError(
				message='File doesn\'t exist',
				cursor_position=len(document.text))


class directoryExist(Validator):
	def validate(self, document):
		ok = os.path.isdir(document.text) if len(document.text) else 1
		if not ok:
			raise ValidationError(
				message='Directory doesn\'t exist',
				cursor_position=len(document.text))




menus_dict = {
"_": [
	{
		"type": "list",
		"name": "list_choice",
		"message": "Home menu",
		"choices": [
			"Generate clients",
			"Deploy server",
			Separator(),
			"Clean Arbitrium's enviroment",
			"Full reset",
			"Exit"
		],
		'filter': lambda val: val.lower().replace(' ', '').replace("'", "")
	}
],

"docker": [
    {
        'type': 'checkbox',
        'message': 'Select features',
        'name': 'docker_settings',
        'choices': [ 
            Separator('= Create clients ='),
            {
                'name': 'Android'
            },
            {
                'name': 'Windows'
            },
            {
                'name': 'Linux'
            },
            Separator('= Deploy servers ='),
            {
                'name': 'serverAPI',
                'disabled': 'required',
                'checked': True
            },
            {
                'name': 'control panel',
                'disabled': 'required',
                'checked': True
            }
        ],
    }
],

"_generateclients_": [
	{
		'type': 'list',
		'name': 'list_choice',
		'message': 'Choose a platform',
		'choices': ['Android', 'Windows', 'Linux'],
		'filter': lambda val: val.lower()
	},
	{
		'type': 'input',
		'name': 'lhost',
		'message': 'Set the server FQDN or IP address [default:127.0.0.1]',
		'validate': DomainValidator
	},
	{
		'type': 'input',
		'name': 'lport',
		'message': 'Set the serverAPI port [default:80]',
		'validate': PortValidator,
	}
],

"_generateclients_android_": [
	{
		'type': 'list',
		'name': 'list_choice',
		'message': 'Do you want to bind it to another app or generate a standalone APK',
		'choices': ['single APK', 'Binder'],
		'filter': lambda val: val.lower().replace(' ', '')
	},
],



"_generateclients_windows_": [
	{
		'type': 'list',
		'name': 'list_choice',
		'message': 'Select client format',
		'choices': ['Exe', 'Python', 'Native(C/C++)'],
		'filter': lambda val: val.replace('(C/C++)', '').lower()
	}
],


"_generateclients_windows_python_": [
	{
	'type': 'confirm',
	'message': 'do you want to obfuscate the client?',
	'name': 'obfuscate',
	'default': False,
	}
],


"_generateclients_windows_exe_": [
	{
	'type': 'confirm',
	'message': 'do you want to obfuscate the client?',
	'name': 'obfuscate',
	'default': False,
	}
],


"_generateclients_linux_": [
	{
		'type': 'list',
		'name': 'list_choice',
		'message': 'Select client format',
		'choices': ['ELF', 'Python', 'Native(C/C++)'],
		'filter': lambda val: val.replace('(C/C++)', '').lower()
	}
],


"_generateclients_linux_python_": [
	{
	'type': 'confirm',
	'message': 'do you want to obfuscate the client?',
	'name': 'obfuscate',
	'default': False,
	}
],


"_generateclients_linux_elf_": [
	{
	'type': 'confirm',
	'message': 'do you want to obfuscate the client?',
	'name': 'obfuscate',
	'default': False,
	}
],



"_generateclients_android_binder_": [
	{
		'type': 'input',
		'name': 'apk_path',
		'message': 'What is the path for APK you want to bind the payload with?',
		'validate': fileExist,
	},
	{
		'type': 'list',
		'name': 'list_choice',
		'message': 'Do you want a release or a debugging version',
		'choices': ['release'],
		'filter': lambda val: val.lower()
	},
],

"_generateclients_android_binder_release_": [
	{
		'type': 'input',
		'name': 'keyalias',
		'message': 'Enter an alias for the key:',
	},
	{
		'type': 'password',
		'name': 'keypass',
		'message': 'Enter a password for the key (will be used to storepass & keystore):',
	},
],



"_generateclients_android_singleapk_": [
	{
		'type': 'input',
		'name': 'src_location',
		'message': 'Enter the absolute path of the app src [default:GIT]:',
		'validate': directoryExist
	},
	{
		'type': 'list',
		'name': 'list_choice',
		'message': 'Do you want a release or a debugging version',
		'choices': ['release', 'debug'],
		'filter': lambda val: val.lower()
	},
],

"_generateclients_android_singleapk_release_": [
	{
		'type': 'input',
		'name': 'keyalias',
		'message': 'Enter an alias for the key:',
	},
	{
		'type': 'password',
		'name': 'keypass',
		'message': 'Enter a password for the key (will be used to storepass & keystore):',
	},
],


"_deployserver_": [
	{
		'type': 'input',
		'name': 'lhost',
		'message': 'Set the server FQDN or IP address [default:127.0.0.1]',
		'validate': DomainValidator
	},
	{
		'type': 'input',
		'name': 'lport',
		'message': 'Set the serverAPI port [default:80]',
		'validate': PortValidator,
	},
	{
		'type': 'input',
		'name': 'webport',
		'message': 'Set the control panel\'s port [default:4321]',
		'validate': PortValidator,
	}
],
}