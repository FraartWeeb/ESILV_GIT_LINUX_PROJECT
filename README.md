# ESILV_GIT_LINUX_PROJECT
This is my project of Git Linux 

# This is the link of my Dashboard : http://16.170.219.132:8050/

Ps : you can activate a moving average by clicking the small button on the dashboard

Or1.sh is the script used for scrapping the data on this website : https://or.fr/cours/or

dashboard5.py is the python code used to create the dashboard

Le code est automatisé à l'aide d'un crontab :

*/5 * * * * /home/ec2-user/Scrapping/Or1.sh

*/2 * * * * python3 /home/ec2-user/Scrapping/dashboard5.py
