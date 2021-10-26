from chromeless import Chromeless

def get_title(self, url):
    self.get(url)
    return self.title

chrome = Chromeless(gateway_url="https://8cm4uhlsme.execute-api.us-east-1.amazonaws.com/prod", gateway_apikey="awpYCGflvR4XJT5ZcOvSt6aA0ndTSJo72jamXzgK")
chrome.attach(get_title)
print(chrome.get_title('http://google.com'))
