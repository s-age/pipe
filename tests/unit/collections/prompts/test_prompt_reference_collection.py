import unittest
from pipe.core.collections.prompts.reference_collection import PromptReferenceCollection
from pipe.core.models.prompts.file_reference import PromptFileReference

class TestPromptReferenceCollection(unittest.TestCase):

    def test_get_content_returns_all_references(self):
        """
        Tests that get_content correctly returns the data from all reference objects.
        (Current implementation does not yet filter by token count).
        """
        references = [
            PromptFileReference(path="file1.txt", content="content1"),
            PromptFileReference(path="file2.txt", content="content2")
        ]
        
        collection = PromptReferenceCollection(references)
        content = collection.get_content()
        
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['path'], "file1.txt")
        self.assertEqual(content[1]['content'], "content2")

    def test_get_content_with_empty_list(self):
        """
        Tests that get_content returns an empty list when initialized with an empty list.
        """
        collection = PromptReferenceCollection([])
        content = collection.get_content()
        self.assertEqual(len(content), 0)

if __name__ == '__main__':
    unittest.main()
