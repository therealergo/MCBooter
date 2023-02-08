# MCBooter
Host powerful Minecraft servers and save money. Automatically launch a Minecraft server on AWS when the user attempts to connect.

# How it Works
MCBooter hosts two servers on AWS, a cheap "Launcher" server and a more powerful Minecraft server. When someone attempts to connect to the launcher server using Minecraft, it uses AWS commands to start the powerful Minecraft server. It then transfers its own elastic IP to the minecraft server. This redirects all traffic to that server, so that once that minecraft server has started up the user can then connect to it.

Once all users leave the Minecraft server, a script running on that server detects that there are no connections and gracefully shuts down the server. The launcher server then detects that the minecraft server is offline, and takes back the elastic IP.

From the user's point of view, they don't have to do anything special. If they're the first person to connect, they'll just have to retry connecting for a minute or two while the server starts up.

# Setup
## Create AWS Resources
1. Create an AWS instance for the Launcher server. We'll call this Server#1 from now on. This instance is always running, but it does not need to be powerful. I use a `t3a.nano` instance since it was the cheapest option when I set this up. I recommend using the Ubuntu AMI image for this instance.
2. Create an AWS instance for the Minecraft server. We'll call this Server#2 from now on. This instance only runs when the server is in use, so for servers that are only used occasionally it can be more powerful without wasting money. I've found that a `t2.medium` instance works well. I recommend using the Ubuntu AMI image for this instance.
3. Create an AWS Elastic IP. If you have a domain name for your server, you'll want to point it at this IP.
4. Configure Server#1 and Server#2 to allow Minecraft ports. If you're just hosting one server, you'll want to open port `25565`.
5. Copy down a few different parameters for each of these AWS resources. You'll need:
 - The allocation id for the Elastic IP.
 - The instance id for the Launcher server.
 - The instance id for the Minecraft server.
 - The name of the AWS region for both servers. The servers must be in the same region.

## Configure Server#1
5. Login to Server#1

6. Install Python requirements
 - `pip install boto3`

7. Setup AWS account access
 - nano `~/.aws/credentials`
 - Fill in `aws_access_key_id`
 - Fill in `aws_secret_access_key`

8. Clone this repo
 - `git clone https://github.com/therealergo/MCBooter.git`
 - `cd MCBooter`

9. Configure settings
 - `cp SettingsTemplate.py Settings.py`
 - `nano Settings.py`
 - You'll now need to fill in the values for `ip_allocationId`, `launcher_instanceId`, `server_instanceId`, and `server_regionName` that you got while setting up the AWS resources.
 - If you are hosting more than one Minecraft server, you should fill in each server's port in `TCP_PORTS`.

10. Setup service
 - `sudo ln ./Launcher.service /etc/systemd/system/Launcher.service`
 - `sudo systemctl enable Launcher`
 - `sudo systemctl start Launcher`
 - You'll have to edit Launcher.service if your username isn't `ubuntu` or if you haven't cloned this repository in the default location.

## Configure Server#2
11. Login to Server#2

12. Clone this repo
 - `git clone https://github.com/therealergo/MCBooter.git`
 - `cd MCBooter`

13. Configure settings
 - `cp SettingsTemplate.py Settings.py`
 - `nano Settings.py`
 - You only need to set the ports here. Set them identically to how you set them in the other settings file.

14. Setup Minecraft Server
 - `mkdir MinecraftServer`
 - `cd MinecraftServer`
 - `wget https://piston-data.mojang.com/v1/objects/c9df48efed58511cdd0213c56b9013a7b5c9ac1f/server.jar`
 - `cd ..`

15. Setup Minecraft server service
 - `sudo ln ./MinecraftServer.service /etc/systemd/system/MinecraftServer.service`
 - `sudo systemctl enable MinecraftServer`
 - `sudo systemctl start MinecraftServer`
 - You'll have to edit MinecraftServer.service if your username isn't `ubuntu` or if you haven't cloned this repository in the default location.

16. Agree to the Minecraft EULA
 - `sudo nano ./MinecraftServer/eula.txt`

17. Setup launcher service
 - `sudo ln ./MCBServer.service /etc/systemd/system/MCBServer.service`
 - `sudo systemctl enable MCBServer`
 - `sudo systemctl start MCBServer`
 - You'll have to edit MCBServer.service if your username isn't `ubuntu` or if you haven't cloned this repository in the default location.
 
 # Note
While I have setup everything here carefully, I am not responsible for the security of your instances or your billing. If someone stays logged into your new Minecraft server for months straight, it will cost more! Please keep an eye on your server, and remember to regularly perform security updates.
