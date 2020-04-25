

def is_user_allowed(user):
    ans = False #презумпция недопуска 
    with open('assigned_bot_users.txt', 'rb') as F: 
        for line in F:
            s = line.decode('utf-8')
            if (s.startswith("#") or s.startswith(' ')) == False:
                s = s.replace('\r','')
                s = s.replace('\n','')
                if user == s:
                    ans = True
                    return ans
    return ans

#далее функции для разрешения  на отдельные комманды
