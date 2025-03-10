from jinja2 import Environment, FileSystemLoader
import pandas as pd

class ReportGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.template = self.env.get_template('report_template.html')
    
    def generate_report(self, results: list) -> str:
        # Convert the flat results list to a structured format for comparison
        tweets = {}
        methods = set()
        
        # First pass: collect all unique tweets and methods
        for result in results:
            tweet = result['tweet']
            method = f"{result['prompt_type']}_{result['llm_model']}"
            
            if tweet not in tweets:
                tweets[tweet] = {}
            
            methods.add(method)
        
        # Second pass: organize results by tweet and method
        for result in results:
            tweet = result['tweet']
            method = f"{result['prompt_type']}_{result['llm_model']}"
            
            tweets[tweet][method] = {
                'prompt': result['prompt'],
                'response': result['response']
            }
        
        # Convert to a format suitable for the template
        structured_results = []
        for tweet, methods_data in tweets.items():
            row = {'tweet': tweet}
            for method in methods:
                if method in methods_data:
                    row[f"{method}_response"] = methods_data[method]['response']
                    row[f"{method}_prompt"] = methods_data[method]['prompt']
                else:
                    row[f"{method}_response"] = "N/A"
                    row[f"{method}_prompt"] = "N/A"
            structured_results.append(row)
        
        # Render the template
        return self.template.render(
            results=structured_results,
            methods=sorted(list(methods)),
            show_prompts=False  # Toggle to show/hide prompts
        ) 