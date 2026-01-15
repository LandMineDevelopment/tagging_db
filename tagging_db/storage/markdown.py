# Placeholder for Markdown storage implementation
# Will parse tags.md and handle file types

class MarkdownStorage:
    def __init__(self, config):
        self.config = config
        self.tags_file = 'tags.md'
    
    def add_tags(self, file_path, tags):
        # TODO: Implement MD writing
        pass
    
    def get_tags(self, file_path):
        # TODO: Implement MD reading
        return []
    
    def search(self, query, type_filter=None):
        # TODO: Implement search
        return {}
    
    def batch_apply(self, folder_path, tag, type_filter=None):
        # TODO: Implement batch
        return 0