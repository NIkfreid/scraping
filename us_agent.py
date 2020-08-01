import random

from scraping.settings.local_settings import BASE_DIR


def choice_useragent():
    user_agents = []
    filename = BASE_DIR + "/user_ag.txt"
    with open(filename, "r", encoding = "utf8") as f:
        agents = f.read().splitlines()
    #print(agents[:100])
    agent = random.choice(agents)
    return agent


if __name__ == '__main__':
    choice_useragent()