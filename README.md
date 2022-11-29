Example Usage: 

    docker run -it --env CPE_UNAME=root --env CPE_PASSWD=root --env CPE_HOSTNAME=192.168.1.1 scraper:latest
    sudo docker pull ghcr.io/mavi0/zyxel-scraper:latest && sudo docker run -it --rm -e CPE_UNAME=root -e CPE_HOSTNAME=192.168.1.1 -e CPE_PASSWD=9fcf67b6 ghcr.io/mavi0/zyxel-scraper:latest