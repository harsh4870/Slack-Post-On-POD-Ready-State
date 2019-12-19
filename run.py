import asyncio
import logging
import time
from kubernetes import client, config, watch
import json
import requests
import time
logger = logging.getLogger('k8s_events')
logger.setLevel(logging.DEBUG)

# If running inside pod
#config.load_incluster_config()

# If running locally
config.load_kube_config()

webhook_url = ''; #Add Slack channel webhook
v1 = client.CoreV1Api()
v1ext = client.ExtensionsV1beta1Api() 
w = watch.Watch()
mydict={}

while True:
	pod_list= v1.list_namespaced_pod("default"); #default namespace
	for i in pod_list.items:
		for c in i.status.container_statuses:
			if(c.ready == True):
				if i.metadata.name in mydict:
					mydict[i.metadata.name]['end_time'] = i.status.conditions[1].last_transition_time;
					dt_started = mydict[i.metadata.name]['start_time'].replace(tzinfo=None);
					dt_ended = mydict[i.metadata.name]['end_time'].replace(tzinfo=None);
					duration = str((dt_ended - dt_started).total_seconds()) + ' Sec';
					fields =  [{"title": "Status", "value": "READY", "short": False }, {"title": "Pod name", "value": i.metadata.name, "short": False }, {"title": "Duration", "value": duration, "short": False }, {"title": "Service name", "value": c.name, "short": False } ] # mydict[i.metadata.name]['duration'] = duration;
					text = c.name + " Pod is started"; 
					data = {"text": text, "mrkdwn": True, "attachments" : [{"color": "#FBBC05", "title": "Pod Details", "fields" : fields, "footer": "Manvar", "footer_icon": "https://harshmanvar123.s3.amazonaws.com/m_logo_slack.png"}, ], }
					response = requests.post(webhook_url, data=json.dumps(data),headers={'Content-Type': 'application/json'});
					del mydict[i.metadata.name]
					if response.status_code != 200:
						raise ValueError('Request to slack returned an error %s, the response is:\n%s' % (response.status_code, response.text));
				time.sleep(1);
			else:
				mydict[i.metadata.name] = {"start_time": i.status.conditions[0].last_transition_time,"end_time": i.status.conditions[1].last_transition_time};
