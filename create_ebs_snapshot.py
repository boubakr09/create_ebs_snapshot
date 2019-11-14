import boto3


#Create an ec2 client
ec2 = boto3.client('ec2')

#get the ec2 instances informations
response = ec2.describe_instances()

#Create a variable for the given machine
given_ec2 = "name_of_ec2_that_contains_the_ebs"

#a for loop to browse those informations
for i in response['Reservations']:

    #create a variable and store the instances ids
    instance_id = (i['Instances'][0]['InstanceId'])
    #create a variable and store the instances tags
    tags = (i['Instances'][0]['Tags'])
    #a loop to browse those tags
    for j in tags:
        #create a variable and store the tag value
        machine = (j['Value'])
        #verify that the given_ec2 name match the tag
        if machine == given_ec2:
            #if so, create a variable and store the block devices
            blockdevicemappings = (i['Instances'][0]['BlockDeviceMappings'])
            #a loop to browse those block devices
            for k in blockdevicemappings:
                ebs = (k['DeviceName'])
                volumeid = (k['Ebs']['VolumeId'])
                #verify that the ec2 instance is not running, if so, stop it first before creating the snapshot
                if (i['Instances'][0]['State']['Name']) == 'running':
                    ec2.stop_instances(InstanceIds=[instance_id])
                    #wait for the ec2 instance to stop
                    waiter = ec2.get_waiter('instance_stopped')
                    waiter.wait(
                        Filters=[
                            {
                                'Name': 'instance-id',
                                'Values': [
                                    instance_id,
                                ]
                            },
                        ],
                    )

                    #create the ebs volume snapshot
                    snapshot = ec2.create_snapshot(
                        Description = given_ec2 + " ebs snapshot for Device : " + ebs,
                        VolumeId = volumeid,
                        TagSpecifications=[
                            {
                                'ResourceType': 'snapshot',
                                'Tags': [
                                    {
                                        'Key' : 'Name',
                                        'Value' : volumeid +'_snapshot'

                                    }
                                ]
                            }
                        ]
                    )
                    #wait for the snapshots to complete before restarting the ec2 instance
                    waiter = ec2.get_waiter('snapshot_completed')
                    waiter.wait()
                    #start the ec2 instance
                    ec2.start_instances(InstanceIds=[instance_id])
