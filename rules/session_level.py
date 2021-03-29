def de_name(session, name_set):
    n = 1
    name_dict = {}
    dialog = []
    for i, utter in enumerate(session):
        seq = []
        for j, word in enumerate(utter.split()):
            if word in name_set:
                if word not in name_dict:
                    name_dict[word] = "<NAME{}>".format(n)
                    n += 1
                seq.append(name_dict[word])
            else:
                seq.append(word)
        dialog.append(" ".join(seq))
    return dialog


def no_short_response(session, min_len=2):
    while session and len(session[-1].replace(" ", "")) < min_len:
        session = session[:-1]
    return session
