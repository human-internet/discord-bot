def homepage(request):
    headers = {'client-id':'SERVER_4R3QUQRNQOSK9TOTWHD7Q2','client-secret':'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'}
    response=requests.post('https://core.human-id.org/v0.0.3/server/users/web-login',headers=headers)
    data=response.json()
    return render(request,'templates/homepage.html',
    {
        'data':data
    })



def callback(request):
    headers = {'client-id':'SERVER_4R3QUQRNQOSK9TOTWHD7Q2','client-secret':'g_zsgbW00owFeQHKmfyXP7p6_iUJ9U797_iThf19AsP-jeZu7DWeGqJ.V3aLRRzm'}
    token = request.GET.get('et')
    response= requests.post('https://core.human-id.org/v0.0.3/server/users/exchange',headers= headers,data={'exchangeToken':token})
    data=response.json()
    return render(request,'templates/index.html',
    {
        'data':data
    })

