

def is_user_allowed(user: str) -> bool:
    with open('assigned_bot_users.txt', 'rb') as file: 
        decoded = map(lambda line: line.decode('utf-8'), file)
        filtered = filter(lambda line: not (line.startswith("#") or 
                                            line.startswith(' ')), 
                          decoded)
        without_specsymbols = map(lambda line: line.replace('\r','')
                                                  .replace('\n',''))
        
        if list(filter(lambda line: line == user)): return True #if no such users with this name found, list will be empty
    
    return False

#далее функции для разрешения  на отдельные комманды
