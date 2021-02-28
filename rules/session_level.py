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
