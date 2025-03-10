from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import time

class ReportGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.template = self.env.get_template('report_template.html')
        self.start_time = time.time()
    
    def format_processing_time(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time < 60:
            return f"{elapsed_time:.1f} seconds"
        else:
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            return f"{minutes}m {seconds}s"
    
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
        
        # Prepare template data
        template_data = {
            'date': datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            'total_tweets': len(tweets),
            'total_models': len(methods),
            'processing_time': self.format_processing_time(),
            'results': structured_results,
            'methods': sorted(list(methods))
        }
        
        # Render the template
        return self.template.render(**template_data)

    def generate_tweet_analysis_html(self, tweet, responses):
        html = f'''
        <div class="tweet-container">
            <div class="tweet-content">
                {tweet}
            </div>
            <div class="responses-grid">
        '''
        
        for model_name, response_data in responses.items():
            html += f'''
                <div class="response-card">
                    <h4>{model_name}</h4>
                    <div class="response">{response_data['response']}</div>
                    <div class="prompt">{response_data['prompt']}</div>
                </div>
            '''
        
        html += '''
            </div>
        </div>
        '''
        return html 