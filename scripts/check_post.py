import urllib.request, re, sys
url = 'http://localhost:8000/communities/post/45/'
try:
    s = urllib.request.urlopen(url).read().decode('utf-8')
except Exception as e:
    print('ERR', e)
    sys.exit(0)
print('moreBtn', bool(re.search('id="moreBtn"', s)))
print('postMenu', bool(re.search('id="postMenu"', s)))
print('dropdown', 'user-profile-dropdown' in s)
print('profileLink', bool(re.search(r'accounts/user/\\d+/profile', s)))
