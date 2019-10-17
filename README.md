# IoT - Create Predictive Maintenance Models To Detect Equipment Breakdown Risks in Maximo

Leverage OSLC and Watson IoT rules to trigger Maximo events

## Description
In this code pattern, we'll demonstrate how to integrate Maximo and Watson IoT Platform to efficiently monitor assets and trigger notifications.

We'll also show how [OSLC](https://www.ibm.com/support/knowledgecenter/en/SSYQBZ_9.5.0/com.ibm.help.common.oslc.doc/topics/c_oslc_overview.html) (Open Services for Lifecycle Collaboration) APIs can be used as a common way to interact with services. In this use case, we'll use these apis to synchronize asset data between services. Finally, we'll demonstrate how to leverage [embedded rules](https://www.ibm.com/support/knowledgecenter/SSQP8H/iot/platform/reference/embeddedrules/rules_api.html) to trigger events when some rule is met.

For example, if an asset malfunctions, we can simultaneously trigger responses in both services: the automated action can create a work order in Maximo, and SMS alerts can be sent out to all interested parties.

<!-- Maximo is a system used for managing assets and workflow processes. This can be used to increase efficiency by automating processes such as work orders, notifications, anomaly detection, etc. -->


## Included Components
* [Maximo](https://www.ibm.com/products/maximo)
* [Watson IoT Platform](https://cloud.ibm.com/catalog/services/internet-of-things-platform)

## Application Workflow Diagram
<img src="https://i.imgur.com/obR4LJG.png">

## Flow
1. Build and deploy OSLC wrapper for Watson IoTP
2. Run script to register devices in Maximo and Watson IoTP
3. Set embedded rules in IoTP
4. As sensor data is received by IoTP, it'll be compared again the rules to see if any conditionals are met. If one or more conditions are met, the corresponding actions should then be executed

# Steps
1. [Provision Maximo EAM](#1-Provision-Maximo-EAM-Instance)
2. [Deploy Cloud Services](#2-deploy-cloud-services)
3. [Build and Deploy OSLC server for Watson IoTP](#3-build-and-deploy-iotp-adaptor)
4. [Register Assets in IoTP and Maximo](#4-register-assets-in-iotp-and-maximo)
5. [Create embedded rules in IoTP](#5-create-embedded-rules-in-iotp)


## Install Prerequisites:
### Python
```
# OS X
brew install python3 python-pip

# Linux
apt-get install python3 python-pip

# Install python packages
pip install python-dotenv
```

### Java
```
# OS X
brew cask install java
brew install maven

# Linux
apt-get install default-jdk
apt-get install maven
```

### Arduino CLI (Optional)
```
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```


### 1. Provision Maximo EAM Instance
To begin, we'll need to provision an instance of Maximo's Enterprise Asset Management system. This system will keep track of higher level assets, such as buildings, vehicles, etc, and allow us to submit work orders when an issue is detected. To provision a free trial version of Maximo, please submit a form at this [link](https://www.ibm.com/account/reg/signup?formid=urx-20869). If you find this pattern useful, you can upgrade to one of the managed Maximo EAM offerings [here](https://www.ibm.com/products/maximo/get-started).


### 2. Deploy Cloud Services
Provision the following services in your IBM Cloud console
* [Watson IoT Platform](https://cloud.ibm.com/catalog/services/internet-of-things-platform)

### 3. Build and Deploy IoTP adaptor
Next, we'll continue on by installing an adaptor that'll allow us to make OSLC calls against the Watson IoT Platform. This will enable us to carry out CRUD operations, make selective queries, service discovery, and [more](https://github.com/OSLC/iotp-adaptor#synopsis).

Begin by downloading apache tomcat, which will serve the adaptor endpoints
```
wget https://www-us.apache.org/dist/tomcat/tomcat-9/v9.0.26/bin/apache-tomcat-9.0.26.tar.gz
```

Next, download the source code for the adaptor from github
```
git clone https://github.com/kkbankol-ibm/iotp-adaptor
```

Build the `iotp-adaptor` binary
```
cd iotp-adaptor/iotp-adaptor
mvn install
```

Confirm that the war file has been successfully built in the target directory
```
ls target/iotp-0.0.1-SNAPSHOT.war
```

Return to your working directory and extract the tomcat folder
```
tar -xzf apache-tomcat-9.0.26.tar.gz
```

Copy the iotp-adaptor war file to the tomcat "webapp" folder, and rename it "iotp.war". When the server starts, this will allow us to access the adaptor endpoints at `/iotp`
```
cp iotp-adaptor/iotp-adaptor/target/iotp-0.0.1-SNAPSHOT.war apache-tomcat-9.0.26/webapp/iotp.war
```

Enter the tomcat bin folder and start the server.
```
cd apache-tomcat-9.0.26/bin
chmod +x startup.sh shutdown.sh catalina.sh
./startup.sh
```

We should now be able to access the iotp-adaptor server at [http://localhost:8081/iotp](http://localhost:8081/iotp). This link should look like so in the browser.

<img src="https://i.imgur.com/V90ycTL.png">

### 4. Register Assets in IoTP and Maximo
After ensuring that our OSLC adaptor is up and running, we can continue by registering assets in Maximo and IoTP.

We'll do this by running the `registerAssets.py` script

```
python3 registerAssets.py
```

This script is interactive, and requests the user to enter a device type and unique ID for the device that is to be registered. This also requires the Maximo URL/Credentials and Watson IoTP org to be placed within an `.env` file in the following format. `max_token` should be the base64 encoded Maximo username and password.
```
iotp_oslc_url=
iotp_org=
maximo_url=
max_token=
```

If this script is successful, we should see the following output

```
Kalonjis-MBP:oslc-pattern kkbankol@us.ibm.com$ python3 registerAsset.py
Please select device
1: Adafruit Feather M0
Device # > 1
Bootstrapping new device of type - adafruit_samd_adafruit_feather_m0
Provide unique device id (or press enter to generate one)

Registering device with id - YVP5N2
Registering device in Watson IoTP via OSLC APIs
IoTP Device Registered
Registering device in Maximo via OSLC APIs
<Response [200]>
{"ASSET":{"rowstamp":"32879403","Attributes":{"ASSETNUM":{"content":"YVP5N2"},"PURCHASEPRICE":{"content":0.0},"REPLACECOST":{"content":0.0},"TOTALCOST":{"content":0.0},"YTDCOST":{"content":0.0},"BUDGETCOST":{"content":0.0},"ISRUNNING":{"content":true},"UNCHARGEDCOST":{"content":0.0},"TOTUNCHARGEDCOST":{"content":0.0},"TOTDOWNTIME":{"content":0.0},"STATUSDATE":{"content":"2019-09-27T18:50:43-05:00"},"CHANGEDATE":{"content":"2019-09-27T18:50:43-05:00"},"CHANGEBY":{"content":"WILSON"},"INVCOST":{"content":0.0},"CHILDREN":{"content":false},"DISABLED":{"content":false},"SITEID":{"content":"BEDFORD"},"ORGID":{"content":"EAGLENA"},"AUTOWOGEN":{"content":false},"ITEMSETID":{"content":"SET1"},"ADDTOSTORE":{"content":false},"MOVEDATE":{"content":"2019-09-27T18:50:43-05:00"},"MOVEDBY":{"content":"WILSON"},"NEWSITE":{"content":"BEDFORD"},"STATUS":{"content":"NOT READY"},"MAINTHIERCHY":{"content":false},"ASSETID":{"content":34571},"MOVED":{"content":false},"NEWASSETNUM":{"content":"YVP5N2"},"ASSETUID":{"content":35061,"resourceid":true},"NEWSTATUS":{"content":"NOT READY"},"HASCHILDREN":{"content":false},"HASPARENT":{"content":false},"OBJECTNAME":{"content":"ASSET"},"LANGCODE":{"content":"EN"},"REPLACEASSETSITE":{"content":"BEDFORD"},"HASLD":{"content":false},"ISLINEAR":{"content":false},"STATUSIFACE":{"content":false},"ASOFDATE":{"content":"2019-09-27T18:50:43-05:00"},"FROMMEASURE":{"content":0.0},"TOMEASURE":{"content":0.0},"ROLLTOALLCHILDREN":{"content":false},"REMOVEFROMACTIVEROUTES":{"content":false},"REMOVEFROMACTIVESP":{"content":false},"CHANGEPMSTATUS":{"content":false},"NEWORGID":{"content":"EAGLENA"},"RETURNEDTOVENDOR":{"content":false},"RELATIONSHIPFILTERBY":{"content":"VIEWALL"},"TLOAMPARTITION":{"content":false},"PLUSCISCONTAM":{"content":false},"PLUSCISINHOUSECAL":{"content":false},"PLUSCISMTE":{"content":false},"PLUSCPMEXTDATE":{"content":false},"PLUSCSOLUTION":{"content":false},"ISCALIBRATION":{"content":false},"EXPECTEDLIFE":{"content":0},"SHOWFROMDATE":{"content":"2019-09-27T00:00:00-05:00"}}}}
Maximo Asset Registered
```

And we can confirm our asset has been created in Maximo and Watson IoTP in their corresponding dashboards
<img src="https://i.imgur.com/B4fOewL.png">


<img src="https://i.imgur.com/8qdg5Ek.png">



### 5. Create embedded rules in IoTP
Now that we have our assets registered we'll next create some embedded rules/actions in the Watson IoT Platform. These will allow actions to automatically be executed in response to incoming data. For example, if we wanted to run some code when IoTP detects high temperature, we can set up a rule with a condition like so.
```
ruleCondition: "$state.temperature > 100"
```

And once our rule is created, we can bind an action to it. In this example, our actions will be a series of webhooks. The first webhook will be used to create a work order in Maximo. The second will be used to send an SMS message.

Below we have printed the Maximo webhook action
```
{
    "name" : "Create Maximo Work Order",
    "description" : "An example webhook action",
    "type": "webhook",
    "enabled": true,
    "configuration": {
        "targetUrl": "{{MAXIMO_URL}}/maxrest/rest/mbo/workorder",
        "method": "POST",
        "contentType": "application/json",
        "username": "{{MAXIMO_USERNAME}}",
        "password": "{{MAXIMO_PASSWORD}}",
        "headers": [
            {
              "name" : 'Content-Type',
              "value": 'application/json'
            }
        ],
        "body" : "{\"description\" : \"Work Order Requested\", \"assetnum\": \"{{ASSET_NUM}}\"}"
    }
}
```

We can upload this action to the IoT platform with a curl command like so
```
curl -X POST -d @templates/maximo-wo-action.json  "http://localhost:8080/iotp/services/iotp/${IOT_ORG}/resources/logicalInterfaceId/action"
```

Next, we'll create a "trigger". This will call the above action every time the condition is met.
```
{  
    "name" : "tempRuleMax",
    "condition" : "$state.temperature > 100",
    "notificationStrategy": {
        "when": "every-time"
    }
}
```

Next, we can upload the trigger to the IoT platform with the following command. Be sure to enter the corresponding device id that will be monitored.
```
curl -X POST -d @templates/maximo-wo-action.json  "http://localhost:8080/iotp/services/iotp/${IOT_ORG}/resources/logicalInterfaceId/trigger/${DEVICE_ID}"
```

If this command completes successfully, the above action should be executed every time a JSON payload containing a "temperature" value above 100 is received. And this action will create a Work Order in Maximo indicating that the corresponding device requires maintenance.


## License
This code pattern is licensed under the Apache Software License, Version 2. Separate third-party code objects invoked within this code pattern are licensed by their respective providers pursuant to their own separate licenses. Contributions are subject to the [Developer Certificate of Origin, Version 1.1 (DCO)](https://developercertificate.org/) and the [Apache Software License, Version 2](https://www.apache.org/licenses/LICENSE-2.0.txt).

[Apache Software License (ASL) FAQ](https://www.apache.org/foundation/license-faq.html#WhatDoesItMEAN)
