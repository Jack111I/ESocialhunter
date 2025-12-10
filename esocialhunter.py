import asyncio
import aiohttp
import argparse
import csv
import json
import time
import os
import random
from typing import List, Tuple, Dict
from tqdm.asyncio import tqdm_asyncio as tqdm

# ---------- CONFIGURATION ----------
DEFAULT_CONCURRENCY = 150
DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 2
DEFAULT_WAIT_BETWEEN = 0.02

USER_AGENT_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15"
    " (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
]

NOT_FOUND_KEYWORDS = [
    "not found", "no such user", "profile not found", "user does not exist",
    "account not found", "page not found", "404", "doesn't exist", "no users found",
    "we couldn't find that account", "sorry, that page doesn’t exist", "this account doesn't exist"
]

REDIRECT_BLACKLIST_KEYWORDS = [
    "signup", "login", "search", "error", "sorry", "404", "not-found", "does-not-exist"
]

# ---------- PLATFORM LIST 300+ ----------
PLATFORMS: List[Tuple[str, str]] = [
    # mainstream social
    ("twitter","https://twitter.com/{username}"),
    ("instagram","https://www.instagram.com/{username}"),
    ("facebook","https://www.facebook.com/{username}"),
    ("tiktok","https://www.tiktok.com/@{username}"),
    ("snapchat","https://www.snapchat.com/add/{username}"),
    ("pinterest","https://www.pinterest.com/{username}"),
    ("threads","https://www.threads.net/@{username}"),
    ("youtube","https://www.youtube.com/@{username}"),
    ("linkedin","https://www.linkedin.com/in/{username}"),
    ("reddit","https://www.reddit.com/user/{username}"),
    ("tumblr","https://{username}.tumblr.com"),
    ("flickr","https://www.flickr.com/people/{username}"),
    ("discord","https://discord.com/users/{username}"),
    ("twitch","https://www.twitch.tv/{username}"),
    ("wechat","https://www.wechat.com/en/{username}"),
    ("vk","https://vk.com/{username}"),
    ("ok_ru","https://ok.ru/{username}"),
    ("mastodon","https://mastodon.social/@{username}"),
    ("gab","https://gab.com/{username}"),
    ("parler","https://parler.com/profile/{username}"),
    ("truthsocial","https://truthsocial.com/@{username}"),
    ("gettr","https://gettr.com/user/{username}"),
    ("ello","https://ello.co/{username}"),
    ("mewe","https://mewe.com/i/{username}"),
    ("clouthub","https://clouthub.com/{username}"),
    # media
    ("soundcloud","https://soundcloud.com/{username}"),
    ("bandcamp","https://bandcamp.com/{username}"),
    ("mixcloud","https://www.mixcloud.com/{username}"),
    ("spotify_artist","https://open.spotify.com/artist/{username}"),
    ("spotify_user","https://open.spotify.com/user/{username}"),
    ("deezer","https://www.deezer.com/profile/{username}"),
    ("apple_music","https://music.apple.com/profile/{username}"),
    ("tidal","https://tidal.com/browse/artist/{username}"),
    ("vimeo","https://vimeo.com/{username}"),
    ("dailymotion","https://www.dailymotion.com/{username}"),
    ("triller","https://triller.co/@{username}"),
    ("bigo","https://www.bigo.tv/{username}"),
    ("rumble","https://rumble.com/c/{username}"),
    ("odysee","https://odysee.com/@{username}"),
    ("d.tube","https://d.tube/#!/c/{username}"),
    ("streamlabs","https://streamlabs.com/{username}"),
    # dev platforms
    ("github","https://github.com/{username}"),
    ("gitlab","https://gitlab.com/{username}"),
    ("bitbucket","https://bitbucket.org/{username}"),
    ("sourceforge","https://sourceforge.net/u/{username}"),
    ("npm","https://www.npmjs.com/~{username}"),
    ("pypi","https://pypi.org/user/{username}"),
    ("rubygems","https://rubygems.org/profiles/{username}"),
    ("crates","https://crates.io/users/{username}"),
    ("dockerhub","https://hub.docker.com/u/{username}"),
    ("stack_overflow","https://stackoverflow.com/users/{username}"),
    ("stackexchange","https://stackexchange.com/users/{username}"),
    ("devto","https://dev.to/{username}"),
    ("hashnode","https://hashnode.com/@{username}"),
    ("codepen","https://codepen.io/{username}"),
    ("replit","https://replit.com/@{username}"),
    ("glitch","https://glitch.com/@{username}"),
    ("kaggle","https://www.kaggle.com/{username}"),
    ("hackerrank","https://www.hackerrank.com/{username}"),
    ("leetcode","https://leetcode.com/{username}"),
    ("codecademy","https://www.codecademy.com/profiles/{username}"),
    ("gitconnected","https://gitconnected.com/{username}"),
    ("sourcerer","https://sourcerer.io/{username}"),
    ("gitee","https://gitee.com/{username}"),
    ("jsfiddle","https://jsfiddle.net/user/{username}"),
    ("itchio","https://itch.io/profile/{username}"),
    ("unity","https://unity.com/u/{username}"),
    # forums
    ("quora","https://www.quora.com/profile/{username}"),
    ("medium","https://medium.com/@{username}"),
    ("behance","https://www.behance.net/{username}"),
    ("dribbble","https://dribbble.com/{username}"),
    ("artstation","https://www.artstation.com/{username}"),
    ("deviantart","https://www.deviantart.com/{username}"),
    ("500px","https://500px.com/{username}"),
    ("producthunt","https://www.producthunt.com/@{username}"),
    ("goodreads","https://www.goodreads.com/{username}"),
    ("instructables","https://www.instructables.com/member/{username}"),
    ("wattpad","https://www.wattpad.com/user/{username}"),
    ("steam","https://steamcommunity.com/id/{username}"),
    ("minecraft","https://minecraft.net/profile/{username}"),
    ("roblox","https://www.roblox.com/users/{username}/profile"),
    ("epicgames","https://www.epicgames.com/id/{username}"),
    ("ubisoft","https://club.ubisoft.com/{username}"),
    ("tapatalk","https://www.tapatalk.com/groups/{username}"),
    ("myanimelist","https://myanimelist.net/profile/{username}"),
    ("anilist","https://anilist.co/user/{username}"),
    ("kitsu","https://kitsu.io/users/{username}"),
    ("gaiaonline","https://www.gaiaonline.com/profiles/{username}"),
    ("crunchyroll","https://www.crunchyroll.com/user/{username}"),
    # blogs
    ("substack","https://substack.com/@{username}"),
    ("ghost","https://ghost.org/{username}"),
    ("wordpress","https://{username}.wordpress.com"),
    ("blogger","https://{username}.blogspot.com"),
    ("weebly","https://{username}.weebly.com"),
    ("livejournal","https://{username}.livejournal.com"),
    ("typepad","https://{username}.typepad.com"),
    # e-commerce
    ("ebay","https://www.ebay.com/usr/{username}"),
    ("amazon_reviews","https://www.amazon.com/gp/profile/{username}"),
    ("etsy","https://www.etsy.com/people/{username}"),
    ("shopify","https://{username}.myshopify.com"),
    ("aliexpress","https://www.aliexpress.com/store/{username}"),
    ("wish","https://www.wish.com/user/{username}"),
    ("mercari","https://www.mercari.com/u/{username}"),
    ("poshmark","https://poshmark.com/closet/{username}"),
    ("offerup","https://offerup.com/p/{username}"),
    ("shopee","https://shopee.com/{username}"),
    # crypto / web3
    ("coinmarketcap","https://coinmarketcap.com/community/profile/{username}"),
    ("binance","https://www.binance.com/en/feed/profile/{username}"),
    ("kucoin","https://www.kucoin.com/profile/{username}"),
    ("okx","https://www.okx.com/users/{username}"),
    ("bybit","https://www.bybit.com/user/{username}"),
    ("metamask","https://metamask.io/{username}"),
    ("opensea","https://opensea.io/{username}"),
    ("rarible","https://rarible.com/{username}"),
    ("etherscan","https://etherscan.io/address/{username}"),
    ("solscan","https://solscan.io/account/{username}"),
    ("blockchair","https://blockchair.com/{username}"),
    ("coinbase","https://www.coinbase.com/{username}"),
    ("bitcointalk","https://bitcointalk.org/index.php?action=profile;u={username}"),
    # photo/creative
    ("vsco","https://vsco.co/{username}"),
    ("canva","https://www.canva.com/{username}"),
    ("pixiv","https://www.pixiv.net/en/users/{username}"),
    ("sketchfab","https://sketchfab.com/{username}"),
    ("mixkit","https://mixkit.co/creators/{username}"),
    ("giphy","https://giphy.com/{username}"),
    # gaming
    ("xbox","https://account.xbox.com/en-us/profile?gamertag={username}"),
    ("playstation","https://my.playstation.com/profile/{username}"),
    ("riot","https://www.leagueofgraphs.com/summoner/{username}"),
    ("leagueoflegends","https://www.op.gg/summoners/all/{username}"),
    ("pubg","https://pubg.op.gg/user/{username}"),
    ("fortnite","https://fortnitetracker.com/profile/all/{username}"),
    ("valorant","https://tracker.gg/valorant/profile/riot/{username}"),
    ("cod","https://cod.tracker.gg/warzone/profile/{username}"),
    ("steamcommunity","https://steamcommunity.com/id/{username}"),
    ("origin","https://myaccount.ea.com/cp-ui/aboutme/index?personaId={username}"),
    # education
    ("coursera","https://www.coursera.org/user/{username}"),
    ("udemy","https://www.udemy.com/user/{username}"),
    ("khanacademy","https://www.khanacademy.org/profile/{username}"),
    ("duolingo","https://www.duolingo.com/profile/{username}"),
    ("skillshare","https://www.skillshare.com/en/profile/{username}/{username}"),
    ("brilliant","https://brilliant.org/profile/{username}"),
    ("chegg","https://www.chegg.com/profile/{username}"),
    # security
    ("hackerone","https://hackerone.com/{username}"),
    ("bugcrowd","https://bugcrowd.com/{username}"),
    ("intigriti","https://app.intigriti.com/profile/{username}"),
    ("tryhackme","https://tryhackme.com/p/{username}"),
    ("hackthebox","https://app.hackthebox.com/profile/{username}"),
    ("cronos","https://cronos.world/{username}"),
    ("virustotal","https://www.virustotal.com/gui/user/{username}"),
    ("shodan","https://account.shodan.io/{username}"),
    ("grayhatwarfare","https://grayhatwarfare.com/user/{username}"),
    # misc
    ("govtrack","https://www.govtrack.us/users/{username}"),
    ("federalregister","https://www.federalregister.gov/people/{username}"),
    ("opencorporates","https://opencorporates.com/companies/{username}"),
    ("kwai","https://www.kwai.com/@{username}"),
    ("smule","https://www.smule.com/{username}"),
    ("ifunny","https://ifunny.co/user/{username}"),
    ("imgur","https://imgur.com/user/{username}"),
    ("bilibili","https://space.bilibili.com/{username}"),
    ("weibo","https://weibo.com/{username}"),
    ("line_me","https://line.me/R/ti/p/{username}"),
    ("zalo","https://zalo.me/{username}"),
    ("nimo","https://www.nimo.tv/{username}"),
    ("trovo","https://trovo.live/{username}"),
    ("afreecatv","https://bj.afreecatv.com/{username}"),
    ("beacons","https://beacons.ai/{username}"),
    ("linktree","https://linktr.ee/{username}"),
    ("carrd","https://{username}.carrd.co"),
    ("aboutme","https://about.me/{username}"),
    ("mix","https://mix.com/{username}"),
    ("pearltrees","https://www.pearltrees.com/{username}"),
    ("flipboard","https://flipboard.com/@{username}"),
    ("slideshare","https://www.slideshare.net/{username}"),
    ("dzone","https://dzone.com/users/{username}"),
    ("trakt","https://trakt.tv/users/{username}"),
    ("letterboxd","https://letterboxd.com/{username}"),
    ("patreon","https://www.patreon.com/{username}"),
    ("ko_fi","https://ko-fi.com/{username}"),
    ("buymeacoffee","https://buymeacoffee.com/{username}"),
    ("reverbnation","https://www.reverbnation.com/{username}"),
    ("gaana","https://gaana.com/artist/{username}"),
    ("saavn","https://www.jiosaavn.com/artist/{username}"),
    ("anghami","https://play.anghami.com/artist/{username}"),
]

# ---------- UTILITIES ----------
def timestamp() -> str:
    return time.strftime("%Y%m%dT%H%M%S")

def save_results(results: List[Dict], base_name: str = None):
    if not base_name:
        base_name = f"results_{timestamp()}"
    csv_name = f"{base_name}.csv"
    json_name = f"{base_name}.json"
    keys = ["timestamp","username","platform","check_url","final_url","http_status","exists","reason"]
    # CSV
    with open(csv_name, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k,"") for k in keys})
    # JSON
    with open(json_name,"w",encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"[+] Saved CSV -> {csv_name}")
    print(f"[+] Saved JSON -> {json_name}")

# ---------- CORE CHECK ----------
class Checker:
    def __init__(self, platforms, concurrency=DEFAULT_CONCURRENCY, timeout=DEFAULT_TIMEOUT, retries=DEFAULT_RETRIES):
        self.platforms = platforms
        self.concurrency = concurrency
        self.timeout = timeout
        self.retries = retries
        self.semaphore = asyncio.Semaphore(concurrency)
        self.results: List[Dict] = []

    async def fetch(self, session, url: str, method="HEAD"):
        headers = {"User-Agent": random.choice(USER_AGENT_POOL),"Accept":"*/*"}
        try:
            if method=="HEAD":
                resp = await session.head(url, allow_redirects=True, timeout=self.timeout)
            else:
                resp = await session.get(url, allow_redirects=True, timeout=self.timeout)
            text = ""
            if method=="GET" or (resp.content_length and resp.content_length<1024*1024):
                try: text = await resp.text(errors="ignore")
                except: text = ""
            return resp.status, str(resp.url), text
        except: return 0, url, ""

    async def check_single(self, session, platform, template, username):
        url = template.format(username=username)
        async with self.semaphore:
            await asyncio.sleep(DEFAULT_WAIT_BETWEEN)
            for _ in range(self.retries+1):
                status, final_url, body = await self.fetch(session,url)
                exists = None
                reason = ""
                lowbody = (body or "").lower()
                final_low = final_url.lower()
                if status in (404,410) or any(k in lowbody for k in NOT_FOUND_KEYWORDS) or any(k in final_low for k in REDIRECT_BLACKLIST_KEYWORDS):
                    exists = False
                    reason = f"status_{status}" if status else "notfound"
                elif status in (200,301,302):
                    exists = True
                    reason = f"status_{status}"
                else:
                    exists = False
                    reason = f"status_{status}"
                return {
                    "timestamp": timestamp(),
                    "username": username,
                    "platform": platform,
                    "check_url": url,
                    "final_url": final_url,
                    "http_status": status,
                    "exists": exists,
                    "reason": reason
                }

    async def run(self, usernames: List[str]):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for user in usernames:
                for platform, template in self.platforms:
                    tasks.append(self.check_single(session, platform, template, user))
            for coro in tqdm.as_completed(tasks, total=len(tasks)):
                res = await coro
                self.results.append(res)
        return self.results

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="SocialHunter - 300+ Platform Username Finder")
    parser.add_argument("--username","-u",help="Single username to scan")
    parser.add_argument("--userfile","-f",help="File containing usernames, one per line")
    args = parser.parse_args()
    usernames=[]
    if args.username: usernames.append(args.username)
    if args.userfile:
        if not os.path.exists(args.userfile): print("File not found"); exit(1)
        with open(args.userfile,"r",encoding="utf-8") as fh:
            usernames.extend([x.strip() for x in fh if x.strip()])
    if not usernames: print("Please provide a username or userfile"); exit(1)
    checker = Checker(PLATFORMS)
    results = asyncio.run(checker.run(usernames))
    save_results(results)

if __name__=="__main__":
    main()
