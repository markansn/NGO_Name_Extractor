import io

import requests, json, os, pdf2image, sys
from PIL import Image
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials
import platform
#use brew to install popper on mac
#CODE BY YANSONG LIU
# global Vars

# Add your Computer Vision subscription key and endpoint to your environment variables.
authsubscription_key = ""
authendpoint = ""
authocr_url = ""

# dicts
generalDict = {}
keywordDict = {}


def assaginaAuthenticationCredentials(subsKey, endPoint, ocr_url):
    global authsubscription_key
    global authendpoint
    global authocr_url
    authsubscription_key = subsKey
    authendpoint = endPoint
    authocr_url = ocr_url


def authenticateClient():
    credentials = CognitiveServicesCredentials(authsubscription_key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=authendpoint, credentials=credentials)
    return text_analytics_client


def key_phrases(doc):
    client = authenticateClient()

    # print('keyphase', ConvertToJSON(doc))
    try:
        response = client.key_phrases(documents=json.loads(ConvertToJSON(doc)))
        return response.documents
    except Exception as err:
        print("Encountered exception. {}".format(err))


def ConvertToJSON(OCRout):
    temp = json.dumps(eval(str(OCRout)))
    return str(temp)


def parseStringToInt(array1, array2):
    for i in range(len(array1)):
        array1[i] = int(array1[i])
    for i in range(len(array2)):
        array2[i] = int(array2[i])
    return array1, array2


def inTheSameParagraph(array1, array2):
    array1, array2 = parseStringToInt(array1, array2)

    limit = 30

    leftBondA1 = array1[0]
    topBondA1 = array1[1]
    widthA1 = array1[2]
    heightA1 = array1[3]

    leftBondA2 = array2[0]
    topBondA2 = array2[1]
    widthA2 = array2[2]
    heightA2 = array2[3]

    if abs((leftBondA1 + widthA1) - leftBondA2) < limit:
        return True
    elif abs((leftBondA2 + widthA2) - leftBondA1) < limit:
        return True
    elif abs((topBondA1 + heightA1) - topBondA2) < limit:
        return True
    elif abs((topBondA2 + heightA2) - topBondA1) < limit:
        return True
    else:
        return False


def OCR2KeyPhrasesReFormatter(OCRout):
    outputString = ""
    outputBuffer = []
    id = 0

    plainText = json.loads(OCRout)
    regions = plainText['regions']
    for region in regions:
        id += 1
        lines = region['lines']
        for line in lines:
            words = line['words']
            for word in words:
                text = word.get('text')
                outputString += text + " "
        temp = json.dumps({'id': id, 'language': 'en', 'text': outputString})
        outputBuffer.append(json.loads(temp))
    return outputBuffer


def callForEachWord(dict, json_text):
    json_dict = json.loads(json_text)
    regions = json_dict['regions']

    for region in regions:
        lines = region['lines']
        for line in lines:
            words = line['words']
            for word in words:
                increaseCounter(dict, word['text'])


def callForEachWordScore(dict, json_text):
    json_dict = json.loads(json_text)
    regions = json_dict['regions']
    scoreDel = 0;

    for region in regions:
        lines = region['lines']
        for line in lines:
            words = line['words']
            for word in words:
                if (search_dict(dict, word['text'])):
                    scoreDel += 5;
    return scoreDel


def search_dict(inputdict, key):
    if key in inputdict:
        return True
    return False


def increaseCounter(inputdict, key):
    if (search_dict(inputdict, key)):
        inputdict[key] += 1
    else:
        inputdict[key] = 1


def getTopValue(dictionary, num_of_items):
    sorted_dict = {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1], reverse=True)}

    first_x_pairs = {k: sorted_dict[k] for k in list(sorted_dict)[:num_of_items]}

    return first_x_pairs


def OCR(image): #!!!
    # Read the image into a byte array
    image_data = image_to_byte_array(image)

    headers = {'Ocp-Apim-Subscription-Key': authsubscription_key, 'Content-Type': 'application/octet-stream'}
    params = {'language': 'unk', 'detectOrientation': 'true'}
    data = image_data
    response = requests.post(authocr_url, headers=headers, params=params, data=data)
    response.raise_for_status()

    return response


def callForEachWordKey(dict, json_text):
    json_text = ConvertToJSON(json_text.replace("None", "\"None\""))
    json_dict = json.loads(ConvertToJSON(json_text))
    key_phrases = json_dict['key_phrases']
    for phrase in key_phrases:
        for word in phrase.split():
            increaseCounter(dict, word)


def callForEachWordKeyReal(dict, json_text):
    json_text = ConvertToJSON(json_text.replace("None", "\"None\""))
    json_dict = json.loads(ConvertToJSON(json_text))
    key_phrases = json_dict['key_phrases']
    scoreDel = 0
    for phrase in key_phrases:
        if search_dict(dict, phrase):
            scoreDel += 1
    return scoreDel


def callForEachWordRealOriginal(inputdict, json_text):
    json_dict = json.loads(json_text)
    regions = json_dict['regions']
    scoreDel = 0

    for region in regions:
        lines = region['lines']
        for line in lines:
            words = line['words']
            for word in words:
                if (search_dict(inputdict, word['text'])):
                    scoreDel += 0.5
    return scoreDel


def getLength(OCRout):
    length = 0
    outputString = ""
    outputBuffer = []
    id = 0

    plainText = json.loads(OCRout)
    regions = plainText['regions']
    for region in regions:
        id += 1
        lines = region['lines']
        for line in lines:
            words = line['words']
            for word in words:
                length += 1
        temp = json.dumps({'id': id, 'language': 'en', 'text': outputString})
        outputBuffer.append(json.loads(temp))
    return length


def trainAlgo(filepath):
    global generalDict
    global keywordDict
    trainingPath = filepath
    print(trainingPath)
    analysis = OCR(trainingPath).json() #!!!
    analysis = ConvertToJSON(analysis)
    analyisReformedForKeyPhases = OCR2KeyPhrasesReFormatter(analysis)
    keywordsList = key_phrases(analyisReformedForKeyPhases)

    # General
    callForEachWord(generalDict, analysis)
    generalDict = getTopValue(generalDict, 200)
    # Key
    for keywords in keywordsList:
        callForEachWordKey(keywordDict, str(keywords))
    # if keywordsList != None:
    #     for keywords in keywordsList:
    #         callForEachWordKey(keywordDict, str(keywords))
    # else:
    #     filepath.show()
    #     print("stop")

    keywordDict = getTopValue(keywordDict, 200)


def extractAlgo(filepath):
    score = 0
    percentage = 0
    realDataPath = filepath
    new_analysis = OCR(realDataPath).json()
    new_analysis = ConvertToJSON(new_analysis)
    analyisReformedForKeyPhasesReal = OCR2KeyPhrasesReFormatter(new_analysis)
    keywordsListReal = key_phrases(analyisReformedForKeyPhasesReal)

    for keywordsReal in keywordsListReal:
        score += callForEachWordKeyReal(keywordDict, str(keywordsReal))
    generalScore = 0
    generalScore += callForEachWordRealOriginal(generalDict, new_analysis)

    score += generalScore
    length = getLength(new_analysis)
    percentage += (score / length) * 100
    if score>130:
        filepath.show()
    return score


def listPdfs(filepath):
    directory = filepath
    pdfs = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdfs.append(os.path.join(directory, filename))
        else:
            continue
    return pdfs


def image_to_byte_array(image: Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def pdfsIterator(pdfs): #returns list of list of images from pdf !!
    pdfStream = []
    pathname = os.path.dirname(sys.argv[0])
    if platform.system() == 'Windows':
        pathname = os.path.abspath(pathname) + os.path.sep + "poppler-0.68.0" + os.path.sep + "bin"

    for pdf in pdfs:

        if platform.system() == 'Windows':
            pages = pdf2image.convert_from_path(pdf, 200, poppler_path=pathname, fmt="jpeg")
        else:
            pages = pdf2image.convert_from_path(pdf, 200, fmt="jpeg")

        pdfStream.append(pages)

    return pdfStream


def trainingWithPath(inputFolder):
    pdfs = listPdfs(inputFolder)
    pdfStream = pdfsIterator(pdfs)
    for pdf in pdfStream:
        for page in pdf:
            trainAlgo(page)


def extractWithPath(inputFolder):
    result = []
    pdfs = listPdfs(inputFolder)
    pdfStream = pdfsIterator(pdfs)
    for pdf in pdfStream:
        score = []
        pageNum = 1
        for page in pdf:
            score.append(str(pageNum)+':'+str(extractAlgo(page)))
            pageNum += 1
    result.append(score)
    return result