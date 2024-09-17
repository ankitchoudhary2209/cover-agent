from jinja2 import Template
import csv
from datetime import datetime
from collections import defaultdict

class ReportGenerator:
    # Enhanced HTML template with additional styling
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Results</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.23.0/themes/prism-okaidia.min.css" rel="stylesheet" />
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 20px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                box-shadow: 0 2px 3px rgba(0,0,0,0.1);
            }
            th, td {
                border: 1px solid #ddd;
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .status-pass {
                color: green;
            }
            .status-fail {
                color: red;
            }
            pre {
                background-color: #000000 !important;
                color: #ffffff !important;
                padding: 5px;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th>Status</th>
                <th>Reason</th>
                <th>Exit Code</th>
                <th>Stderr</th>
                <th>Stdout</th>
                <th>Test</th>
            </tr>
            {% for result in results %}
            <tr>
                <td class="status-{{ result.status }}">{{ result.status }}</td>
                <td>{{ result.reason }}</td>
                <td>{{ result.exit_code }}</td>
                <td>{% if result.stderr %}<pre><code class="language-shell">{{ result.stderr }}</code></pre>{% else %}&nbsp;{% endif %}</td>
                <td>{% if result.stdout %}<pre><code class="language-shell">{{ result.stdout }}</code></pre>{% else %}&nbsp;{% endif %}</td>
                <td>{% if result.test %}<pre><code class="language-python">{{ result.test[] }}</code></pre>{% else %}&nbsp;{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.23.0/prism.min.js"></script>
    </body>
    </html>
    """

    @classmethod
    def generate_report(cls, results, file_path,source_file_path,prev_coverage,new_coverage):
        """
        Renders the HTML report with given results and writes to a file.

        :param results: List of dictionaries with test results.
        :param file_path: Path to the HTML file where the report will be written.
        """
        template = Template(cls.HTML_TEMPLATE)
        html_content = template.render(results=results)
        with open(file_path, "w") as file:
            file.write(html_content)
        file_exists = False
        report_path = 'report.csv'
        counters = {
            'total': 0,
            'passed and added to the test file': 0,
            'failed': 0,
            'build/setup failed': 0,
            'Passed but did not increase code coverage': 0,
        }
        for result in results:
            counters["total"] += 1
            print(result)
            if result["reason"] == "Skipping a generated test that failed due to Build/Setup Failure":
                counters["build/setup failed"] += 1
            elif result["reason"] == "Skipping a generated test that failed":
                counters["failed"] += 1
            elif result["reason"] == "Coverage did not increase":
                counters["Passed but did not increase code coverage"] += 1
            else:
                counters["passed"] += 1
        try:
            with open(report_path, 'r') as f:
                file_exists = True
        except FileNotFoundError:
            file_exists = False
        data = {
            'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Total Test Cases': counters['total'],
            'Passed': counters['passed and added to the test file'],
            'Failed (Build/Setup/Errored)': counters['build/setup failed'],
            'Failed (Other)': counters['failed'],
            'Source File' : source_file_path,
            'Previouse Coverage': f'{round(prev_coverage * 100, 2)}%',
            'New Coverage' :f'{round(new_coverage * 100, 2)}%'
        }
        with open(report_path, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()  # Write header only if the file is new
            writer.writerow(data)
