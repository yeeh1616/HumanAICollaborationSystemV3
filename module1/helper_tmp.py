from module1.helper import cos_two_sentences

answer = 'Policymakers throughout England, UK are hesitant to include school closures in the national lockdown due to learning loss for students that is hard to make up and therefore has potential long-term consequences; as well as much bigger implications for lower socio-economic groups that will widen inequality and reduce social mobility.'


def get_highlighted_tmp(sentences):
    threshold = 0.5
    highlighted = []
    for sentence in sentences:
        cosine = cos_two_sentences(answer, sentence)
        if cosine > threshold:
            highlighted.append([sentence, True])
        else:
            highlighted.append([sentence, False])
    return answer, highlighted


def set_selection_AI_tmp(q):
    for option in q['options']:
        option['checked'] = 'False'
        option['cos'] = 0.00000

        if option['option'] == "Closure and Regulations of Schools.":
            option['cos'] = 0.999999
            option['checked'] = 'True'

def set_completation_AI_tmp(q):
    topN = q['answers']
    for i in range(0, len(topN)):
        if 'UK' in topN[i][0]:
            # topN[i][0] ='United Kingdom'
            topN[i][1] = 0.99999
            topN.sort(reverse=True, key=lambda y: y[1])
