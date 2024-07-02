
class ParseMessage:
    def __init__(self) -> None:
        self.lastParsed = None

    def parseToDictionary(self, rawInput):
        # Replace 'false' with 'False' before using eval
        cleaned_input = self.checkAndReplaceBool(rawInput)
        
        # Use eval on the cleaned input
        result = eval(cleaned_input)

        # Store the result in self.lastParsed
        self.lastParsed = result

        return result

    def checkAndReplaceBool(self, input_str):
        input_str=input_str.replace('false', 'False')
        input_str=input_str.replace('true', 'True')        
        # Replace 'false' with 'False' in the input string
        return input_str

#XML

'''
import xml.etree.ElementTree as ET

class XMLBuilder:
    def __init__(self, root_tag):
        self.root = ET.Element(root_tag)

    def add_element(self, parent, tag, text=None, attributes=None):
        element = ET.SubElement(parent, tag, attributes)
        if text:
            element.text = text
        return element

    def to_string(self):
        return ET.tostring(self.root, encoding='utf-8').decode('utf-8')

# Example usage:
xml_builder = XMLBuilder('bookstore')

book1 = xml_builder.add_element(xml_builder.root, 'book', attributes={'category': 'fiction'})
xml_builder.add_element(book1, 'title', 'The Great Gatsby')
xml_builder.add_element(book1, 'author', 'F. Scott Fitzgerald')
xml_builder.add_element(book1, 'price', '15.99')

book2 = xml_builder.add_element(xml_builder.root, 'book', attributes={'category': 'non-fiction'})
xml_builder.add_element(book2, 'title', 'Sapiens: A Brief History of Humankind')
xml_builder.add_element(book2, 'author', 'Yuval Noah Harari')
xml_builder.add_element(book2, 'price', '24.99')

xml_string = xml_builder.to_string()
print(xml_string)
'''

class ParseXML(ParseMessage):
    def __init__(
            self,
            frame=["",""] #XML template
        ) -> None:
        super().__init__()

    def parseIn(self,message):
        return (self.frame[0] + message + self.frame[1])

class ParseJSONBase(ParseMessage):
    def __init__(self) -> None:
        super().__init__()

class ParseJSON(ParseJSONBase):
    def __init__(self) -> None:
        super().__init__()

    def parseIn(self,JSON): #returns dictionary
       return eval(JSON)
    
    def parseOut(self,dict):
        return ('"' + str(dict) + '"')

'''Example

this = '{"payload":"sf10Vapourtec1", "mode":"FLOW", "flowrate": 0.5}'

thisThing = ParseJSON().parseIn('{"payload":"sf10Vapourtec1", "mode":"FLOW", "flowrate": 0.5}')

thatThing = ParseJSON().parseOut(thisThing)

print ((this) + "\n" + str(thisThing) + "\n" + thatThing)

'''
'''
thisExample='{"payload":"reactIR702L1","data":[],"timestamp":"1704789924805"}'
thisExample=ParseMessage().parseToDictionary(thisExample)
print(thisExample)
'''