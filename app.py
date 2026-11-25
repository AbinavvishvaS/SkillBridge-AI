import os
import sqlite3
import uuid
import re
from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-key-change-before-deployment")
DB_PATH = os.path.join(app.instance_path, "skillbridge.db")
os.makedirs(app.instance_path, exist_ok=True)

# 6 Professional Career Tracks
CAREER_SKILLS = {
    "Data Analyst": ["Python", "SQL", "Excel", "Statistics", "Data Visualization", "Data Cleaning"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Git", "TypeScript", "Responsive Design"],
    "Python Developer": ["Python", "OOP", "SQL", "Flask", "Git", "REST APIs"],
    "Machine Learning Engineer": ["Python", "Statistics", "Machine Learning", "Pandas", "Scikit-learn", "Deep Learning"],
    "Full-Stack Developer": ["HTML", "CSS", "JavaScript", "React", "Python", "SQL", "Git", "REST APIs"],
    "Cloud & DevOps Engineer": ["Linux", "Git", "Docker", "CI/CD", "Python", "Cloud Fundamentals"]
}

# 5 Core Competency Dimensions for Spider / Radar Chart
SKILL_DIMENSIONS = {
    "Python": "Coding & Syntax",
    "JavaScript": "Coding & Syntax",
    "HTML": "Coding & Syntax",
    "CSS": "Coding & Syntax",
    "TypeScript": "Coding & Syntax",
    "OOP": "Coding & Syntax",
    
    "SQL": "Data & Databases",
    "Excel": "Data & Databases",
    "Pandas": "Data & Databases",
    "Data Cleaning": "Data & Databases",
    
    "React": "Frameworks & Systems",
    "Flask": "Frameworks & Systems",
    "REST APIs": "Frameworks & Systems",
    "Responsive Design": "Frameworks & Systems",
    
    "Statistics": "Problem Solving & Math",
    "Data Visualization": "Problem Solving & Math",
    "Machine Learning": "Problem Solving & Math",
    "Scikit-learn": "Problem Solving & Math",
    "Deep Learning": "Problem Solving & Math",
    
    "Git": "DevOps & Tooling",
    "Linux": "DevOps & Tooling",
    "Docker": "DevOps & Tooling",
    "CI/CD": "DevOps & Tooling",
    "Cloud Fundamentals": "DevOps & Tooling"
}

# Estimated Hours to Bridge Each Skill
SKILL_HOURS = {
    "Python": 14, "SQL": 12, "Excel": 8, "Statistics": 10, "Data Visualization": 8, "Data Cleaning": 6,
    "HTML": 6, "CSS": 10, "JavaScript": 16, "React": 18, "Git": 6, "TypeScript": 12, "Responsive Design": 6,
    "OOP": 8, "Flask": 10, "REST APIs": 8, "Machine Learning": 20, "Pandas": 8, "Scikit-learn": 12, "Deep Learning": 24,
    "Linux": 10, "Docker": 12, "CI/CD": 8, "Cloud Fundamentals": 14
}

LEARNING_RESOURCES = {
    "Python": "Practise variables, data structures, generator expressions, modular functions, and automation scripts.",
    "SQL": "Practise SELECT, filtering, complex JOINs, window functions, GROUP BY, and schema indexing.",
    "Excel": "Master XLOOKUP, dynamic PivotTables, nested logical formulas, and interactive dashboard charts.",
    "Statistics": "Study hypothesis testing, confidence intervals, p-values, distributions, and variance.",
    "Data Visualization": "Build accessible, narrative-driven visualizations (scatter, heatmaps, interactive dashboards).",
    "Data Cleaning": "Detect missing values, treat outliers with IQR, standardize date formats, and deduplicate records.",
    "HTML": "Build semantic, accessible (WCAG AA), screen-reader friendly landmark page architectures.",
    "CSS": "Master modern CSS Grid, Flexbox, custom properties, responsive media queries, and fluid animations.",
    "JavaScript": "Master ES6+, closures, the event loop, Promises, async/await, and reactive DOM rendering.",
    "React": "Build component hierarchies, custom hooks, context state management, and memoized rendering.",
    "TypeScript": "Enforce strict types, interfaces, generics, union types, and type-safe API communication.",
    "Responsive Design": "Implement fluid viewports, mobile-first layouts, accessible touch targets, and flexible media.",
    "Git": "Master feature branching, atomic commits, rebasing, pull requests, and resolving merge conflicts.",
    "OOP": "Apply SOLID principles, design patterns, inheritance, polymorphism, and encapsulated models.",
    "Flask": "Build RESTful route handlers, Jinja templates, session authentication, and database migrations.",
    "REST APIs": "Design idempotent endpoints, HTTP status codes, JSON validation, rate limiting, and documentation.",
    "Machine Learning": "Master train/validation/test splits, cross-validation, regularization, and performance metrics.",
    "Pandas": "Transform tabular data, apply vectorised operations, merge DataFrames, and aggregate metrics.",
    "Scikit-learn": "Author ColumnTransformer pipelines, StandardScaler, and GridSearchCV cross-validation.",
    "Deep Learning": "Understand backpropagation, activation functions, CNNs/Transformers, and loss optimization.",
    "Linux": "Master Bash shell commands, SSH, file permissions, cron daemons, systemctl, and process management.",
    "Docker": "Write multi-stage Dockerfiles, configure docker-compose, mount volumes, and manage containers.",
    "CI/CD": "Configure automated GitHub Actions workflows, linting checks, unit test suites, and staging deploys.",
    "Cloud Fundamentals": "Understand cloud compute (VMs/containers), IAM policies, object storage, and cloud networking."
}

MISSIONS = [
    {"id":"py-functions","title":"Python Function Builder","skill":"Python","level":"Beginner","points":20,"task":"Write a function named calculate_total that accepts two numbers and returns their sum.","hint":"Define a function with def, accept two parameters, and return the result.","answer":"def calculate_total(a, b):\n    return a + b"},
    {"id":"sql-filter","title":"SQL Filter Detective","skill":"SQL","level":"Beginner","points":20,"task":"Write an SQL query to select name and score from students whose score is at least 80.","hint":"Use SELECT, FROM, and a WHERE condition.","answer":"SELECT name, score FROM students WHERE score >= 80;"},
    {"id":"html-semantic","title":"Semantic HTML Starter","skill":"HTML","level":"Beginner","points":15,"task":"Create a semantic HTML page structure with header, main and footer elements.","hint":"Use the three semantic elements and close each tag.","answer":"<header></header>\n<main></main>\n<footer></footer>"},
    {"id":"js-array","title":"JavaScript Array Explorer","skill":"JavaScript","level":"Intermediate","points":25,"task":"Write JavaScript to create an array of three skills and print each skill using forEach.","hint":"Create an array and call its forEach method.","answer":"const skills = ['HTML', 'CSS', 'JavaScript'];\nskills.forEach(skill => console.log(skill));"},
    {"id":"stats-mean","title":"Statistics Quick Check","skill":"Statistics","level":"Beginner","points":15,"task":"Find the mean of 4, 6 and 8. Explain the calculation.","hint":"Add the values and divide by how many values there are.","answer":"(4 + 6 + 8) / 3 = 6"},
    {"id":"pandas-clean","title":"Pandas Data Cleaner","skill":"Pandas","level":"Intermediate","points":25,"task":"Write one Pandas statement to remove rows containing missing values from a DataFrame named df.","hint":"Look for the DataFrame dropna method.","answer":"df = df.dropna()"},
    {"id":"sql-join","title":"SQL Relational Join Master","skill":"SQL","level":"Intermediate","points":30,"task":"Write an SQL query joining orders with customers on customer_id to show customer name and order amount.","hint":"Use INNER JOIN and ON orders.customer_id = customers.id.","answer":"SELECT customers.name, orders.amount\nFROM orders\nINNER JOIN customers ON orders.customer_id = customers.id;"},
    {"id":"py-dict-comp","title":"Python Dictionary Comprehension","skill":"Python","level":"Intermediate","points":25,"task":"Given a list numbers = [1, 2, 3], write a comprehension to create a dict mapping each number to its square.","hint":"Use {n: n**2 for n in numbers}.","answer":"squared = {n: n**2 for n in [1, 2, 3]}"},
    {"id":"docker-build","title":"Docker Containerization Quickstart","skill":"Docker","level":"Intermediate","points":30,"task":"Write a minimal Dockerfile command to copy all files from current directory to /app inside container.","hint":"Use the COPY instruction.","answer":"COPY . /app"},
    {"id":"git-branch","title":"Git Feature Branch Workflow","skill":"Git","level":"Beginner","points":20,"task":"Write the Git command to create and switch to a new branch named 'feature-auth'.","hint":"Use git checkout -b or git switch -c.","answer":"git checkout -b feature-auth"}
]

INTERVIEW_QUESTIONS = {
    "Data Analyst": [
        ("How would you handle missing values in a dataset?", "Look for a structured answer: inspect missingness patterns (MCAR, MAR, MNAR), decide between deletion or imputation (median, mode, model-based), and document impact."),
        ("What is the difference between INNER JOIN and LEFT JOIN?", "A strong answer explains that INNER JOIN returns only records with matches in both tables, whereas LEFT JOIN preserves all rows from the primary table, filling NULLs where right matches do not exist."),
        ("How would you explain a dashboard to a non-technical stakeholder?", "A strong answer identifies the stakeholder goal, leads with the primary headline metric, translates technical nuances into plain business outcomes, and provides clear action steps.")
    ],
    "Frontend Developer": [
        ("What is the difference between HTML, CSS and JavaScript?", "A strong answer describes HTML as document structure, CSS as visual layout/presentation, and JavaScript as dynamic behaviour and asynchronous logic."),
        ("Why is responsive design important?", "A strong answer mentions fluid grids, viewport flexibility, mobile-first design, touch targets, accessibility, and testing across diverse devices."),
        ("How would you debug a button that does not respond?", "A strong answer systematically checks: element selector matching, event listener attachment, JavaScript console errors, CSS pointer-events or z-index blocking, and network failures.")
    ],
    "Python Developer": [
        ("What is the difference between a list and a tuple in Python?", "A strong answer explains that lists are mutable (can modify) and use square brackets, while tuples are immutable (hashable, memory efficient, can be dict keys)."),
        ("What is a Python dictionary?", "A strong answer describes hash-map based key-value pairs offering O(1) average lookup time, keys must be hashable, and demonstrates safe retrieval with .get()."),
        ("Why should errors be handled with try and except?", "A strong answer explains graceful recovery from predictable failures, avoiding crashes, logging meaningful context, and cautioning against catching bare Exception without handling.")
    ],
    "Machine Learning Engineer": [
        ("Why do we split data into training, validation and test sets?", "A strong answer explains training fits parameters, validation tunes hyperparameters and guards against early overfitting, and test provides an unbiased measure of generalisation on unseen data."),
        ("What is overfitting and how do you prevent it?", "A strong answer explains that overfitting occurs when a model memorises noise of training data. Prevention: regularization (L1/L2, Dropout), cross-validation, pruning, or gathering more data."),
        ("Why is a baseline model useful?", "A strong answer explains that it provides a fast, interpretable benchmark (e.g. predicting the mean or majority class) to prove whether complex models actually deliver genuine predictive lift.")
    ],
    "Full-Stack Developer": [
        ("How do you architect communication between a React frontend and a Python backend?", "A strong answer discusses RESTful or GraphQL endpoints, JSON serialization, HTTP status codes, CORS headers, state synchronization, and handling loading/error states gracefully."),
        ("What are the key differences between SQL and NoSQL databases?", "A strong answer explains structured schema, ACID transactions, and relational joins in SQL vs flexible schema, horizontal scalability, and eventual consistency in NoSQL.")
    ],
    "Cloud & DevOps Engineer": [
        ("What is the difference between a Virtual Machine and a Docker container?", "A strong answer explains VMs virtualize hardware and include a full guest OS, whereas containers share the host kernel, isolating processes at the OS level for instant startup and low overhead."),
        ("Why is Continuous Integration and Continuous Deployment (CI/CD) essential?", "A strong answer emphasizes automated testing, catching integration bugs early, rapid feedback loops, reproducible builds, and safe, zero-downtime releases.")
    ]
}

CURATED_DOUBTS = [
    {
        "id": "sql-inner-vs-left-join",
        "category": "SQL & Databases",
        "question": "What is the exact difference between INNER JOIN and LEFT JOIN, and when do NULLs appear?",
        "short_answer": "INNER JOIN returns only rows where the join condition matches in BOTH tables. LEFT JOIN returns ALL rows from the left table, plus matched columns from the right table (filling NULL where no match exists).",
        "detailed_explanation": "Think of INNER JOIN as an intersection (A ∩ B). If a customer has never placed an order, they are excluded completely. LEFT JOIN guarantees you never lose any records from your primary (left) table. If a customer has 0 orders, their row is kept, and order columns show NULL. Use LEFT JOIN when asking 'show me all customers and their orders if any' or to find records with no matches ('WHERE orders.id IS NULL').",
        "code_example": "-- INNER JOIN: Only customers with orders\nSELECT c.name, o.order_id\nFROM customers c\nINNER JOIN orders o ON c.id = o.customer_id;\n\n-- LEFT JOIN: ALL customers, even those with zero orders\nSELECT c.name, o.order_id\nFROM customers c\nLEFT JOIN orders o ON c.id = o.customer_id;\n\n-- Find customers who NEVER ordered:\nSELECT c.name\nFROM customers c\nLEFT JOIN orders o ON c.id = o.customer_id\nWHERE o.order_id IS NULL;",
        "common_pitfall": "Putting a WHERE filter on a right-table column (like 'WHERE o.status = \"shipped\"') after a LEFT JOIN accidentally turns it back into an INNER JOIN, because NULL values get filtered out! Use the condition in the ON clause instead.",
        "confidence_score": 99,
        "quiz_question": "If Customer 'Alice' has 0 orders, will Alice appear in the result of 'SELECT * FROM customers c INNER JOIN orders o ON c.id = o.customer_id'?",
        "quiz_answer": "No. Alice will be excluded because INNER JOIN requires a matching row in the right table."
    },
    {
        "id": "sql-where-vs-having",
        "category": "SQL & Databases",
        "question": "When should I use WHERE vs HAVING in an SQL query?",
        "short_answer": "WHERE filters individual rows BEFORE aggregation (GROUP BY). HAVING filters aggregated groups AFTER aggregation.",
        "detailed_explanation": "The SQL query execution lifecycle processes WHERE first, filtering rows from the raw table. Then GROUP BY groups the remaining rows. Finally, HAVING evaluates conditions on aggregate functions like COUNT(), SUM(), AVG(), or MAX(). You cannot use aggregate functions inside a WHERE clause (e.g. 'WHERE COUNT(order_id) > 5' is invalid syntax).",
        "code_example": "SELECT department, AVG(salary) AS avg_sal\nFROM employees\nWHERE status = 'Active'         -- Filters individual rows BEFORE grouping\nGROUP BY department\nHAVING AVG(salary) > 75000;    -- Filters aggregated groups AFTER calculation",
        "common_pitfall": "Filtering on non-aggregated columns inside HAVING. While some SQL dialects allow it, it degrades performance. Always filter raw rows early with WHERE to reduce the data volume before GROUP BY.",
        "confidence_score": 98,
        "quiz_question": "Can you write 'WHERE SUM(sales) > 1000' in SQL?",
        "quiz_answer": "No! Aggregate functions like SUM() must be filtered using HAVING, not WHERE."
    },
    {
        "id": "py-equality-vs-identity",
        "category": "Python & Programming",
        "question": "What is the difference between '==' and 'is' in Python?",
        "short_answer": "'==' checks for equality of VALUE (do they hold the same data?). 'is' checks for IDENTITY (do they point to the exact same object in memory?).",
        "detailed_explanation": "When you write 'a == b', Python calls the '__eq__' method to compare values. When you write 'a is b', Python checks 'id(a) == id(b)'. Two distinct lists with identical elements are equal ('==') but not identical ('is'). Always use 'is' when checking against singletons like 'None' ('if x is None:'). Never use 'is' for number or string comparisons.",
        "code_example": "list1 = [1, 2, 3]\nlist2 = [1, 2, 3]\n\nprint(list1 == list2)  # True (identical content)\nprint(list1 is list2)  # False (different memory addresses)\n\n# Correct idiom for singletons:\nx = None\nif x is None:\n    print('x is safely identified as None')",
        "common_pitfall": "Assuming 'x is 1000' will behave like 'x == 1000'. Python caches small integers (-5 to 256), so 'is' might coincidentally return True for small numbers but False for 1000, creating subtle, hard-to-find bugs.",
        "confidence_score": 99,
        "quiz_question": "If a = [1] and b = [1], what does 'a is b' evaluate to?",
        "quiz_answer": "False! They are two distinct objects stored in different memory locations."
    },
    {
        "id": "py-mutable-default-args",
        "category": "Python & Programming",
        "question": "Why shouldn't I use a mutable default argument like `def add_item(item, items=[])` in Python?",
        "short_answer": "Default arguments are evaluated ONCE when the function definition is loaded, NOT each time the function is called. All calls share the exact same list instance!",
        "detailed_explanation": "When Python defines a function, default parameters are created as persistent objects stored in the function's '__defaults__' attribute. If that object is mutable (a list, dictionary, or set), any mutation persists across subsequent function calls, leading to ghost values accumulating.",
        "code_example": "# BAD PRACTICE: Accumulates values across calls\ndef append_bad(x, target=[]):\n    target.append(x)\n    return target\n\n# GOOD PRACTICE: Use None as default and create a fresh instance\ndef append_good(x, target=None):\n    if target is None:\n        target = []\n    target.append(x)\n    return target\n\nprint(append_good(1))  # [1]\nprint(append_good(2))  # [2] - clean and independent!",
        "common_pitfall": "Thinking default values reset every invocation. Always use 'target=None' and assign inside the function body.",
        "confidence_score": 100,
        "quiz_question": "When are default argument expressions evaluated in Python?",
        "quiz_answer": "At definition/import time once, not at call time."
    },
    {
        "id": "frontend-useeffect-loops",
        "category": "Frontend & Web Development",
        "question": "Why does my React `useEffect` trigger an infinite loop and how do I fix it?",
        "short_answer": "An infinite loop occurs when `useEffect` updates a state variable that is also listed in its dependency array (or when no dependency array is supplied at all).",
        "detailed_explanation": "When React renders, it checks if values in the `useEffect` dependency array changed by reference ('Object.is'). If you set state inside useEffect without a dependency array, every render triggers useEffect, which triggers another render infinitely. If you pass an object or array created inline without 'useMemo' or 'useCallback', its reference changes on every render, triggering useEffect continuously.",
        "code_example": "// ❌ BAD: Infinite loop\nuseEffect(() => {\n  fetchData().then(data => setData(data));\n}); // No dependency array!\n\n// ✅ GOOD: Runs only once on mount\nuseEffect(() => {\n  let isMounted = true;\n  fetchData().then(data => {\n    if (isMounted) setData(data);\n  });\n  return () => { isMounted = false; }; // Cleanup\n}, []); // Empty array runs once on mount",
        "common_pitfall": "Omitting functions from dependencies or defining functions inside the component body without wrapping them in 'useCallback', causing dependency checks to fail on every render.",
        "confidence_score": 98,
        "quiz_question": "What happens if you omit the second argument (dependency array) in `useEffect`?",
        "quiz_answer": "The effect executes after EVERY single render, causing an infinite loop if it sets state."
    },
    {
        "id": "frontend-flexbox-vs-grid",
        "category": "Frontend & Web Development",
        "question": "When should I use CSS Flexbox vs CSS Grid?",
        "short_answer": "Use Flexbox for 1-dimensional layouts (a single row OR column). Use CSS Grid for 2-dimensional layouts (rows AND columns simultaneously).",
        "detailed_explanation": "Flexbox is content-out: items dictate their own size and flow linearly along the main axis. It is ideal for navigation bars, button groups, icon alignments, and centered cards. CSS Grid is layout-in: you define columns and rows first, and items slot into that rigid or responsive matrix. It is ideal for overall page structure, photo galleries, dashboard widgets, and complex card layouts.",
        "code_example": "/* Flexbox: 1D linear alignment */\n.navbar {\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n}\n\n/* CSS Grid: 2D responsive matrix */\n.dashboard-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));\n  gap: 20px;\n}",
        "common_pitfall": "Trying to force Flexbox to align both rows and columns across multiple lines with complex percentage widths, which leads to wrapping alignment quirks. Switch to Grid when 2D alignment matters.",
        "confidence_score": 97,
        "quiz_question": "Which layout model is best suited for a 2-dimensional dashboard with coordinated rows and columns?",
        "quiz_answer": "CSS Grid."
    },
    {
        "id": "ml-overfitting-vs-underfitting",
        "category": "Machine Learning & AI",
        "question": "How do I diagnose whether my model is Overfitting or Underfitting, and how do I fix each?",
        "short_answer": "Underfitting = High Training Error & High Test Error (model too simple). Overfitting = Very Low Training Error & High Test Error (model memorised noise).",
        "detailed_explanation": "In Underfitting (High Bias), the model cannot capture underlying trends (e.g. fitting a straight line to an exponential curve). Fix: Use a more complex model, add polynomial features, or decrease regularization. In Overfitting (High Variance), the model fits training samples so closely that it fails to generalize to unseen test data. Fix: Add regularization (L1/L2, Dropout), prune tree depth, use early stopping, or acquire more diverse training data.",
        "code_example": "# High Variance / Overfitting diagnostic:\n# Train Accuracy: 99.4% | Validation Accuracy: 71.2% (Huge gap!)\n\n# Fix with Regularization and Early Stopping:\nfrom sklearn.ensemble import RandomForestClassifier\n\n# Restrict tree depth to prevent leaf-level memorisation\nmodel = RandomForestClassifier(\n    n_estimators=100,\n    max_depth=6,         # Prevents infinite branching\n    min_samples_leaf=5,  # Requires at least 5 samples per leaf\n    random_state=42\n)",
        "common_pitfall": "Evaluating model performance solely on the training dataset. Always validate using k-fold cross-validation or a strictly separated holdout test split.",
        "confidence_score": 99,
        "quiz_question": "If your model scores 99% accuracy on training data but only 68% on test data, what is it suffering from?",
        "quiz_answer": "Overfitting (High Variance)."
    },
    {
        "id": "ml-precision-vs-recall",
        "category": "Machine Learning & AI",
        "question": "What is the difference between Precision and Recall, and how do I choose between them?",
        "short_answer": "Precision = 'Of all items predicted positive, how many were actually positive?' Recall = 'Of all actual positive items, how many did we successfully find?'",
        "detailed_explanation": "Precision = TP / (TP + FP). Optimize Precision when the cost of a False Positive is severe (e.g. Spam detection). Recall = TP / (TP + FN). Optimize Recall when the cost of a False Negative is fatal (e.g. Cancer detection or fraud).",
        "code_example": "from sklearn.metrics import classification_report\nprint(classification_report(y_true, y_pred))",
        "common_pitfall": "Using simple Accuracy on imbalanced datasets.",
        "confidence_score": 98,
        "quiz_question": "In medical screening for a critical illness, should you prioritise Precision or Recall?",
        "quiz_answer": "Recall, because failing to detect an ill patient (False Negative) can be life-threatening."
    },
    {
        "id": "stats-correlation-vs-causation",
        "category": "Data Analysis & Statistics",
        "question": "Why doesn't correlation imply causation, and how do I prove a real causal relationship?",
        "short_answer": "Correlation measures how two variables move together statistically. Causation means change in variable X directly causes the change in variable Y.",
        "detailed_explanation": "Confounding variables often mimic correlation. To establish causation, you need controlled A/B testing or randomized controlled trials (RCTs).",
        "code_example": "import pandas as pd\ncorrelation = df['metric_a'].corr(df['metric_b'])\nprint(f'Correlation coefficient: {correlation:.2f}')",
        "common_pitfall": "Presenting high correlation to stakeholders as proof of causation without an A/B test.",
        "confidence_score": 98,
        "quiz_question": "What is the gold standard method in data science to establish true causation?",
        "quiz_answer": "A randomized controlled experiment (A/B testing)."
    },
    {
        "id": "git-merge-vs-rebase",
        "category": "Git & Version Control",
        "question": "What is the difference between `git merge` and `git rebase`?",
        "short_answer": "`git merge` combines branches and creates a new merge commit, preserving historical chronology. `git rebase` rewrites commit history by moving your feature branch commits to the tip of main.",
        "detailed_explanation": "Merge preserves complete historical truth. Rebase creates a clean, linear commit history. Never rebase commits that have been pushed to a shared public branch!",
        "code_example": "# Merge approach:\ngit checkout main\ngit merge feature-branch\n\n# Rebase approach:\ngit checkout feature-branch\ngit rebase main",
        "common_pitfall": "Rebasing a shared branch that teammates have pulled, invalidating commit hashes.",
        "confidence_score": 99,
        "quiz_question": "What is the primary risk of using `git rebase` on a shared public branch?",
        "quiz_answer": "It rewrites commit history and hashes, breaking repositories for collaborating team members."
    }
]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def workspace_id():
    if "workspace_id" not in session:
        session["workspace_id"] = str(uuid.uuid4())
    return session["workspace_id"]

def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS passport (
            id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL,
            kind TEXT NOT NULL, title TEXT NOT NULL, url TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS mission_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL,
            mission_id TEXT NOT NULL, answer TEXT NOT NULL, completed_at TEXT NOT NULL,
            UNIQUE(workspace, mission_id)
        );
        CREATE TABLE IF NOT EXISTS sprint_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL,
            week_start TEXT NOT NULL, skill TEXT NOT NULL, task TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS interview_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL,
            career TEXT NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL,
            self_rating INTEGER NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS doubts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL,
            doubt_ref TEXT NOT NULL DEFAULT '', category TEXT NOT NULL,
            question TEXT NOT NULL, short_answer TEXT NOT NULL,
            detailed_explanation TEXT NOT NULL, code_example TEXT NOT NULL DEFAULT '',
            common_pitfall TEXT NOT NULL DEFAULT '', confidence_score INTEGER NOT NULL DEFAULT 95,
            is_cleared INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS confidence_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL,
            career TEXT NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL,
            percentage INTEGER NOT NULL, feedback TEXT NOT NULL, created_at TEXT NOT NULL
        );
        """)
        
init_db()

def get_points():
    wid = session.get("workspace_id")
    if not wid: return 0
    with db() as conn:
        done_missions = {r["mission_id"] for r in conn.execute("SELECT mission_id FROM mission_completions WHERE workspace=?", (wid,))}
        cleared_doubts = conn.execute("SELECT COUNT(*) AS c FROM doubts WHERE workspace=? AND is_cleared=1", (wid,)).fetchone()["c"]
    mission_pts = sum(m["points"] for m in MISSIONS if m["id"] in done_missions)
    doubt_pts = cleared_doubts * 15
    return mission_pts + doubt_pts

def calculate_confidence_index(wid):
    with db() as conn:
        missions_count = conn.execute("SELECT COUNT(*) n FROM mission_completions WHERE workspace=?", (wid,)).fetchone()["n"]
        passport_count = conn.execute("SELECT COUNT(*) n FROM passport WHERE workspace=?", (wid,)).fetchone()["n"]
        sprint_done = conn.execute("SELECT COUNT(*) n FROM sprint_tasks WHERE workspace=? AND done=1", (wid,)).fetchone()["n"]
        interview_count = conn.execute("SELECT COUNT(*) n FROM interview_attempts WHERE workspace=?", (wid,)).fetchone()["n"]
        doubts_cleared = conn.execute("SELECT COUNT(*) n FROM doubts WHERE workspace=? AND is_cleared=1", (wid,)).fetchone()["n"]
        latest_quiz = conn.execute("SELECT percentage FROM confidence_tests WHERE workspace=? ORDER BY id DESC LIMIT 1", (wid,)).fetchone()

    mission_factor = min(30, missions_count * 6)
    doubt_factor = min(25, doubts_cleared * 8)
    evidence_factor = min(25, (passport_count * 5) + (sprint_done * 4))
    quiz_val = latest_quiz["percentage"] if latest_quiz else 0
    interview_factor = min(20, (interview_count * 4) + round(quiz_val * 0.1))

    total_score = min(100, max(15, mission_factor + doubt_factor + evidence_factor + interview_factor))
    
    tier = "Foundational Learner"
    if total_score >= 85: tier = "High-Confidence Expert"
    elif total_score >= 70: tier = "Job-Ready Explorer"
    elif total_score >= 50: tier = "Active Skill Builder"
    elif total_score >= 30: tier = "Promising Apprentice"

    return {
        "score": total_score,
        "tier": tier,
        "missions_count": missions_count,
        "passport_count": passport_count,
        "doubts_cleared": doubts_cleared,
        "interview_count": interview_count,
        "sprint_done": sprint_done,
        "breakdown": {
            "Missions & Hands-on": f"{mission_factor}/30",
            "Doubt Clearance & Clarity": f"{doubt_factor}/25",
            "Evidence & Sprint Tasks": f"{evidence_factor}/25",
            "Interview & Quiz Validation": f"{interview_factor}/20"
        }
    }

def analyze_skills_multi_dimensional(career, selected_skills, proficiencies=None):
    if proficiencies is None: proficiencies = {}
    required = CAREER_SKILLS.get(career, CAREER_SKILLS["Data Analyst"])
    selected_set = set(selected_skills)
    
    matching = [s for s in required if s in selected_set]
    missing = [s for s in required if s not in selected_set]
    raw_readiness = round((len(matching) / len(required)) * 100) if required else 0
    
    proficiency_sum = 0
    matching_detailed = []
    for s in matching:
        level_str = proficiencies.get(s, "Proficient")
        weight = 0.8
        if level_str == "Mastered": weight = 1.0
        elif level_str == "Familiar": weight = 0.5
        proficiency_sum += weight
        matching_detailed.append({"skill": s, "level": level_str, "weight": int(weight * 100)})
        
    weighted_readiness = round((proficiency_sum / len(required)) * 100) if required else 0
    
    gap_matrix = []
    total_hours = 0
    for idx, s in enumerate(missing):
        hrs = SKILL_HOURS.get(s, 10)
        total_hours += hrs
        if idx < 2: priority, badge = "Critical Core", "tag-danger"
        elif idx < 4: priority, badge = "High-Value", "tag-warning"
        else: priority, badge = "Complementary", "tag-info"
            
        gap_matrix.append({
            "skill": s, "priority": priority, "badge": badge, "hours": hrs,
            "action": LEARNING_RESOURCES.get(s, "Practise with a targeted portfolio build.")
        })
        
    weeks_to_ready = max(1, round(total_hours / 8)) if total_hours > 0 else 0
    
    multi_role_matches = {}
    for role_name, skills_list in CAREER_SKILLS.items():
        matched_in_role = sum(1 for sk in skills_list if sk in selected_set)
        multi_role_matches[role_name] = round((matched_in_role / len(skills_list)) * 100)
        
    other_roles = {r: p for r, p in multi_role_matches.items() if r != career}
    top_alt_role = max(other_roles.items(), key=lambda x: x[1]) if other_roles else (career, raw_readiness)
    transferability_score = round(sum(other_roles.values()) / len(other_roles)) if other_roles else raw_readiness
    
    dimensions = ["Coding & Syntax", "Data & Databases", "Frameworks & Systems", "Problem Solving & Math", "DevOps & Tooling"]
    radar_scores = {}
    for dim in dimensions:
        dim_skills = [s for s, d in SKILL_DIMENSIONS.items() if d == dim]
        if dim_skills:
            acquired = sum(1 for s in dim_skills if s in selected_set)
            radar_scores[dim] = round((acquired / len(dim_skills)) * 100)
        else:
            radar_scores[dim] = 0

    return {
        "career": career, "readiness": raw_readiness, "weighted_readiness": weighted_readiness,
        "matching": matching, "matching_detailed": matching_detailed, "missing": missing,
        "gap_matrix": gap_matrix, "total_hours": total_hours, "weeks_to_ready": weeks_to_ready,
        "required_count": len(required), "matched_count": len(matching),
        "multi_role_matches": multi_role_matches, "top_alt_role": top_alt_role[0],
        "top_alt_percent": top_alt_role[1], "transferability_score": transferability_score,
        "radar_scores": radar_scores,
        "roadmap": [{"skill": s, "action": LEARNING_RESOURCES.get(s, "Practise with a small project.")} for s in missing]
    }

def resolve_doubt_ai(query, category="General"):
    clean_query = query.strip().lower()
    best_match = None
    best_score = 0
    for cd in CURATED_DOUBTS:
        q_tokens = set(re.findall(r'\w+', cd["question"].lower()))
        input_tokens = set(re.findall(r'\w+', clean_query))
        overlap = len(q_tokens.intersection(input_tokens))
        if overlap > best_score:
            best_score = overlap
            best_match = cd

    if best_match and best_score >= 3:
        return {
            "category": best_match["category"], "question": best_match["question"],
            "short_answer": best_match["short_answer"], "detailed_explanation": best_match["detailed_explanation"],
            "code_example": best_match["code_example"], "common_pitfall": best_match["common_pitfall"],
            "accuracy_score": best_match["confidence_score"]
        }

    detected_cat = "Programming & Concepts"
    code_snippet = ""
    pitfall = "Skipping edge-case tests or relying on undocumented assumptions."
    
    if any(k in clean_query for k in ["sql", "join", "select", "table", "query", "database", "group by", "index"]):
        detected_cat = "SQL & Databases"
        short = f"For '{query}': In relational databases, enforce proper indexing, filter early with WHERE, and explicitly define join constraints."
        detailed = (
            f"When tackling questions regarding {query}, always follow the relational lifecycle:\n"
            "1. Identify primary and foreign key constraints between entities.\n"
            "2. Filter raw records early with WHERE before expensive GROUP BY or aggregations.\n"
            "3. Use explain plans (EXPLAIN ANALYZE) to verify index usage over full sequential scans.\n"
            "4. Mind NULL propagation: equality checks with NULL return NULL; use IS NULL instead."
        )
        code_snippet = "-- Structured, safe SQL pattern:\nSELECT primary_id, COUNT(*) AS total_records\nFROM your_table\nWHERE status = 'ACTIVE' AND deleted_at IS NULL\nGROUP BY primary_id\nHAVING COUNT(*) > 1;"
        pitfall = "Treating NULL values as zeroes or empty strings; in SQL, arithmetic with NULL yields NULL."
        confidence = 97

    elif any(k in clean_query for k in ["python", "list", "dict", "tuple", "decorator", "yield", "async", "def", "lambda"]):
        detected_cat = "Python & Programming"
        short = f"In Python: '{query}' is resolved cleanly using idiomatic constructs, immutable records, and pure functions."
        detailed = (
            f"Regarding your question on {query}:\n"
            "1. Python prioritizes explicit syntax over implicit behavior (The Zen of Python).\n"
            "2. Keep functions deterministic: avoid unexpected mutation of parameter arguments.\n"
            "3. Leverage generators and comprehensions to avoid memory bloat on large collections.\n"
            "4. Employ specific exception handling rather than catching bare Exception."
        )
        code_snippet = "# Clean Python implementation pattern:\ndef process_data(items: list) -> list:\n    return [item.strip().capitalize() for item in items if item]"
        pitfall = "Mutating a list or dictionary while iterating directly over it, which triggers runtime bugs."
        confidence = 98

    elif any(k in clean_query for k in ["docker", "container", "image", "volume", "compose", "kubernetes", "linux"]):
        detected_cat = "Cloud & DevOps"
        short = f"For '{query}': Ensure minimal image layers, immutable container state, and decoupled secrets management."
        detailed = (
            f"Here is how to solve {query} cleanly:\n"
            "1. Leverage multi-stage builds to keep production images lightweight.\n"
            "2. Never bake secrets or API tokens directly into Dockerfiles; inject them at runtime via environment variables.\n"
            "3. Map persistent volumes for stateful data and keep containers ephemeral.\n"
            "4. Run containers with non-root user privileges for security hardening."
        )
        code_snippet = "# Clean Multi-stage Dockerfile:\nFROM python:3.11-slim as builder\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD [\"python\", \"app.py\"]"
        pitfall = "Using ':latest' tags in production; always pin exact image tags to ensure reproducible deployments."
        confidence = 96

    elif any(k in clean_query for k in ["react", "component", "state", "props", "hook", "dom", "css", "html", "javascript", "typescript"]):
        detected_cat = "Frontend & Web Development"
        short = f"For '{query}': Maintain unidirectional data flow, encapsulate state at the closest shared parent, and keep markup semantic."
        detailed = (
            f"Here is the breakdown for {query}:\n"
            "1. Treat state as immutable; always use updater functions.\n"
            "2. Avoid direct DOM queries; let the virtual DOM reconciler handle layout updates.\n"
            "3. Always clean up timers or subscriptions inside useEffect return functions.\n"
            "4. Adhere to WCAG AA accessibility standards and responsive flex/grid layouts."
        )
        code_snippet = "// React clean pattern\nconst [value, setValue] = useState('');\nconst handleChange = (e) => { setValue(e.target.value); };\nreturn <input value={value} onChange={handleChange} placeholder='Clean state' />;"
        pitfall = "Directly modifying state objects (e.g. `state.count = 5`) instead of invoking the setter."
        confidence = 97

    elif any(k in clean_query for k in ["model", "train", "test", "metric", "accuracy", "data", "regression", "classification", "loss", "deep learning"]):
        detected_cat = "Machine Learning & AI"
        short = f"For '{query}': Guarantee strict separation between training and test sets to prevent data leakage, and benchmark against simple heuristics."
        detailed = (
            f"Accurate ML resolution for {query}:\n"
            "1. Prevent Data Leakage: fit all transformations (scaling, encoders, imputers) exclusively on training folds.\n"
            "2. Choose metrics aligned with business penalties (e.g. ROC-AUC, Precision/Recall over raw accuracy).\n"
            "3. Inspect residual plots and feature importances to verify the model captures genuine signal.\n"
            "4. Use cross-validation to verify stability across splits."
        )
        code_snippet = "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\n\npipeline = Pipeline([\n    ('scaler', StandardScaler()),\n    ('classifier', LogisticRegression())\n])\npipeline.fit(X_train, y_train)"
        pitfall = "Fitting scalers on the entire dataset prior to splitting into train/test, causing target leakage."
        confidence = 96

    else:
        detected_cat = category if category != "General" else "Core Engineering"
        short = f"Core Principle for '{query}': Deconstruct into inputs, desired outputs, system constraints, and validated best practices."
        detailed = (
            f"Structured resolution for: {query}\n"
            "1. Core Principle: Define the fundamental rule governing this system behavior.\n"
            "2. Step-by-Step Resolution: Isolate assumptions with a minimal test case and verify against official documentation.\n"
            "3. Validation: Test boundary edge conditions (null, extreme ranges) to build complete confidence."
        )
        code_snippet = "# Verification step:\n# 1. State hypothesis\n# 2. Test minimal reproducible case\n# 3. Confirm expected outcome"
        pitfall = "Relying on guesswork instead of structured isolation and verified documentation."
        confidence = 95

    return {
        "category": detected_cat, "question": query, "short_answer": short,
        "detailed_explanation": detailed, "code_example": code_snippet,
        "common_pitfall": pitfall, "accuracy_score": confidence
    }

@app.context_processor
def inject_globals():
    wid = workspace_id()
    conf = calculate_confidence_index(wid)
    return {
        "total_points": get_points(),
        "today": date.today().isoformat(),
        "confidence_score": conf["score"],
        "confidence_tier": conf["tier"]
    }

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    wid = workspace_id()
    
    if request.method == "POST":
        career = request.form.get("career", "")
        selected_skills = request.form.getlist("skills")
        if career not in CAREER_SKILLS:
            error = "Please select a valid career track."
        else:
            proficiencies = {}
            for s in selected_skills:
                lvl = request.form.get(f"prof_{s}", "Proficient")
                proficiencies[s] = lvl
                
            result = analyze_skills_multi_dimensional(career, selected_skills, proficiencies)
            session["last_career"] = career
            session["last_missing"] = result["missing"]
            session["last_selected_skills"] = selected_skills

    all_skills = sorted({s for skills in CAREER_SKILLS.values() for s in skills})
    
    return render_template(
        "index.html",
        careers=list(CAREER_SKILLS),
        all_skills=all_skills,
        result=result,
        error=error,
        skill_dimensions=SKILL_DIMENSIONS
    )

# REST API: Instant Floating Doubt Resolution
@app.route("/api/resolve-doubt", methods=["POST"])
def api_resolve_doubt():
    data = request.get_json() or {}
    query = data.get("question", "").strip()
    category = data.get("category", "General")
    
    if not query or len(query) < 4:
        return jsonify({"status": "error", "message": "Please enter a specific question (minimum 4 characters)."}), 400
        
    resolved = resolve_doubt_ai(query, category)
    wid = workspace_id()
    
    with db() as conn:
        conn.execute("""
        INSERT INTO doubts (workspace, doubt_ref, category, question, short_answer, detailed_explanation, code_example, common_pitfall, confidence_score, is_cleared, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            wid,
            str(uuid.uuid4())[:8],
            resolved["category"],
            resolved["question"],
            resolved["short_answer"],
            resolved["detailed_explanation"],
            resolved["code_example"],
            resolved["common_pitfall"],
            resolved.get("accuracy_score", resolved.get("confidence_score", 95)),
            date.today().isoformat()
        ))
        
    conf = calculate_confidence_index(wid)
    new_points = get_points()
    
    return jsonify({
        "status": "success",
        "result": resolved,
        "resolved": resolved,
        "new_points": new_points,
        "confidence_score": conf["score"],
        "confidence_tier": conf["tier"]
    })

# REST API: Interactive Skill What-If Simulator
@app.route("/api/simulate-skill", methods=["POST"])
def api_simulate_skill():
    data = request.get_json() or {}
    career = data.get("career", "Data Analyst")
    current_skills = data.get("current_skills", [])
    simulated_skill = data.get("simulated_skill", "").strip()
    
    combined_skills = list(set(current_skills + ([simulated_skill] if simulated_skill else [])))
    analysis = analyze_skills_multi_dimensional(career, combined_skills)
    
    # Accept 'acquired_skills' field too (used by simulator chip buttons)
    acquired_skills = data.get("acquired_skills", current_skills)
    combined_skills = list(set(acquired_skills + ([simulated_skill] if simulated_skill else [])))
    analysis2 = analyze_skills_multi_dimensional(career, combined_skills)

    return jsonify({
        "status": "success",
        "analysis": analysis,
        "match_percentage": analysis2["readiness"],
        "gap_count": len(analysis2["missing"]),
        "estimated_study_hours": analysis2["total_hours"],
        "percentage_delta": analysis2["readiness"] - analysis["readiness"],
        "competency_radar": analysis2["radar_scores"]
    })

@app.route("/doubts", methods=["GET", "POST"])
def doubts():
    wid = workspace_id()
    search_query = request.args.get("q", "").strip()
    active_category = request.args.get("category", "All")

    if request.method == "POST":
        user_doubt = request.form.get("question", "").strip()
        user_cat = request.form.get("category", "General")
        if not user_doubt or len(user_doubt) < 5:
            flash("Please enter a specific question or doubt (minimum 5 characters).", "error")
        else:
            resolved = resolve_doubt_ai(user_doubt, user_cat)
            with db() as conn:
                conn.execute("""
                INSERT INTO doubts (workspace, doubt_ref, category, question, short_answer, detailed_explanation, code_example, common_pitfall, confidence_score, is_cleared, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                """, (
                    wid,
                    str(uuid.uuid4())[:8],
                    resolved["category"],
                    resolved["question"],
                    resolved["short_answer"],
                    resolved["detailed_explanation"],
                    resolved["code_example"],
                    resolved["common_pitfall"],
                    resolved.get("accuracy_score", resolved.get("confidence_score", 95)),
                    date.today().isoformat()
                ))
            flash(f"✦ Doubt resolved with {resolved['confidence_score']}% Accuracy! Marked as cleared (+15 pts).", "success")
            return redirect(url_for("doubts"))

    with db() as conn:
        user_doubts = conn.execute("SELECT * FROM doubts WHERE workspace=? ORDER BY id DESC", (wid,)).fetchall()

    categories = ["All", "SQL & Databases", "Python & Programming", "Frontend & Web Development", "Machine Learning & AI", "Data Analysis & Statistics", "Git & Version Control", "Cloud & DevOps", "My Doubts"]

    filtered_curated = []
    for cd in CURATED_DOUBTS:
        match_cat = (active_category == "All" or active_category == cd["category"])
        match_query = True
        if search_query:
            term = search_query.lower()
            match_query = (term in cd["question"].lower() or term in cd["short_answer"].lower() or term in cd["category"].lower())
        if match_cat and match_query:
            filtered_curated.append(cd)

    cleared_refs = {d["question"] for d in user_doubts if d["is_cleared"] == 1}

    return render_template(
        "doubts.html",
        curated_doubts=filtered_curated,
        user_doubts=user_doubts,
        cleared_refs=cleared_refs,
        categories=categories,
        active_category=active_category,
        search_query=search_query
    )

@app.post("/doubts/toggle/<int:doubt_id>")
def toggle_doubt(doubt_id):
    wid = workspace_id()
    with db() as conn:
        row = conn.execute("SELECT is_cleared FROM doubts WHERE id=? AND workspace=?", (doubt_id, wid)).fetchone()
        if row:
            new_state = 0 if row["is_cleared"] == 1 else 1
            conn.execute("UPDATE doubts SET is_cleared=? WHERE id=? AND workspace=?", (new_state, doubt_id, wid))
            msg = "Doubt marked as Cleared! Confidence boosted (+15 pts)." if new_state == 1 else "Doubt reopened for review."
            flash(msg, "success" if new_state == 1 else "notice")
    return redirect(url_for("doubts"))

@app.post("/doubts/clear-curated")
def clear_curated():
    wid = workspace_id()
    qid = request.form.get("curated_id")
    doubt_obj = next((d for d in CURATED_DOUBTS if d["id"] == qid), None)
    if doubt_obj:
        with db() as conn:
            existing = conn.execute("SELECT id, is_cleared FROM doubts WHERE workspace=? AND question=?", (wid, doubt_obj["question"])).fetchone()
            if existing:
                conn.execute("UPDATE doubts SET is_cleared=1 WHERE id=?", (existing["id"],))
            else:
                conn.execute("""
                INSERT INTO doubts (workspace, doubt_ref, category, question, short_answer, detailed_explanation, code_example, common_pitfall, confidence_score, is_cleared, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                """, (
                    wid,
                    doubt_obj["id"],
                    doubt_obj["category"],
                    doubt_obj["question"],
                    doubt_obj["short_answer"],
                    doubt_obj["detailed_explanation"],
                    doubt_obj["code_example"],
                    doubt_obj["common_pitfall"],
                    doubt_obj["confidence_score"],
                    date.today().isoformat()
                ))
        flash(f"✓ Concept '{doubt_obj['question'][:38]}...' marked as 100% Cleared! +15 Confidence Points awarded.", "success")
    return redirect(url_for("doubts"))

@app.route("/confidence", methods=["GET", "POST"])
def confidence():
    wid = workspace_id()
    career = session.get("last_career", "Data Analyst")
    conf = calculate_confidence_index(wid)

    QUIZ_SETS = {
        "Data Analyst": [
            {
                "q": "Which SQL clause is used to filter rows after an aggregation like SUM() or COUNT()?",
                "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
                "correct": "HAVING",
                "explain": "HAVING evaluates aggregated expressions after GROUP BY, whereas WHERE filters individual rows prior to aggregation."
            },
            {
                "q": "When is median preferred over mean to measure central tendency?",
                "options": ["When data has extreme outliers or heavy skew", "When data is perfectly symmetric", "When sample size is under 10", "Median is never preferred"],
                "correct": "When data has extreme outliers or heavy skew",
                "explain": "The median is robust against extreme values/outliers, whereas the mean is heavily pulled by extreme values."
            },
            {
                "q": "In Python Pandas, which method removes rows containing missing NaN values?",
                "options": ["df.clean()", "df.dropna()", "df.remove_nulls()", "df.pop()"],
                "correct": "df.dropna()",
                "explain": "dropna() drops rows containing null/NaN values according to the specified axis and threshold."
            },
            {
                "q": "Which chart type is best suited to display the distribution of a single continuous variable?",
                "options": ["Pie Chart", "Histogram", "Scatter Plot", "Stacked Bar"],
                "correct": "Histogram",
                "explain": "Histograms group continuous data into bins to reveal spread, skewness, and modality."
            }
        ],
        "Frontend Developer": [
            {
                "q": "What is the key advantage of CSS Grid over Flexbox?",
                "options": ["Grid handles 2D (rows + columns) simultaneously", "Grid is supported on older browsers", "Grid replaces HTML", "Grid only works on buttons"],
                "correct": "Grid handles 2D (rows + columns) simultaneously",
                "explain": "CSS Grid is a two-dimensional layout system, whereas Flexbox is primarily one-dimensional."
            },
            {
                "q": "Which HTTP method should be used when submitting a form that updates server data?",
                "options": ["GET", "POST", "OPTIONS", "TRACE"],
                "correct": "POST",
                "explain": "POST sends state-changing payloads in the request body rather than exposing them in the URL string."
            },
            {
                "q": "What happens if you update state in React without a setter function?",
                "options": ["It re-renders automatically", "React ignores the update and no re-render is triggered", "It throws a syntax error", "The browser crashes"],
                "correct": "React ignores the update and no re-render is triggered",
                "explain": "React state is immutable; mutating state directly does not alert the reconciler to trigger a UI re-render."
            },
            {
                "q": "Which HTML element provides the most semantic landmark for the main page content?",
                "options": ["<div id='content'>", "<main>", "<section class='body'>", "<article-body>"],
                "correct": "<main>",
                "explain": "<main> is the standard ARIA Landmark element representing the dominant content of the <body>."
            }
        ],
        "Python Developer": [
            {
                "q": "Which data structure is immutable and can be used as a dictionary key?",
                "options": ["list", "tuple", "set", "dict"],
                "correct": "tuple",
                "explain": "Tuples containing only immutable elements are hashable and can safely serve as dictionary keys."
            },
            {
                "q": "What keyword turns a standard Python function into a Generator?",
                "options": ["return", "yield", "generator", "async def"],
                "correct": "yield",
                "explain": "Using 'yield' produces a value and suspends execution state, yielding values on demand via the iterator protocol."
            },
            {
                "q": "What is the time complexity of looking up a key in a Python dictionary on average?",
                "options": ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
                "correct": "O(1)",
                "explain": "Python dictionaries are hash tables providing average O(1) constant time lookups."
            },
            {
                "q": "Why should you avoid mutable default arguments like `def func(items=[])`?",
                "options": ["Python will throw a SyntaxError", "The default list is created once at definition and shared across all calls", "It runs 10x slower", "It leaks memory"],
                "correct": "The default list is created once at definition and shared across all calls",
                "explain": "Default arguments are bound at function definition time, causing mutations to persist across subsequent invocations."
            }
        ],
        "Machine Learning Engineer": [
            {
                "q": "What diagnostic pattern indicates a model is overfitting?",
                "options": ["High training error and high test error", "Near-zero training error but high test error", "Identical train and test error", "Low accuracy on all folds"],
                "correct": "Near-zero training error but high test error",
                "explain": "A large divergence between near-perfect training scores and poor validation/test scores is the hallmark of overfitting."
            },
            {
                "q": "Why must scalers and encoders be fit ONLY on the training fold during cross-validation?",
                "options": ["To avoid data leakage from the test distribution", "Because scikit-learn forbids it", "To save GPU memory", "It has no impact"],
                "correct": "To avoid data leakage from the test distribution",
                "explain": "Fitting transformations on the test set leaks global statistics into the model."
            },
            {
                "q": "Which metric should you optimize when False Negatives are far more dangerous than False Positives?",
                "options": ["Precision", "Recall", "Accuracy", "Specificity"],
                "correct": "Recall",
                "explain": "Recall measures the proportion of actual positives caught (TP / (TP + FN)), minimizing missed cases."
            },
            {
                "q": "What technique randomly deactivates neurons during neural network training to reduce co-adaptation?",
                "options": ["Batch Normalization", "Dropout", "Early Stopping", "Gradient Clipping"],
                "correct": "Dropout",
                "explain": "Dropout randomly zeroes neuron activations during forward passes to enforce robust feature learning."
            }
        ],
        "Full-Stack Developer": [
            {
                "q": "What does CORS stand for and where is it enforced?",
                "options": ["Cross-Origin Resource Sharing, enforced by the Browser", "Central Origin Routing System, enforced by the Server", "Client-Oriented Rendering Standard, enforced by React", "Cross-Operation Redux State, enforced by JavaScript"],
                "correct": "Cross-Origin Resource Sharing, enforced by the Browser",
                "explain": "CORS is a browser security mechanism that restricts HTTP requests initiated from scripts to outside domains unless permitted."
            },
            {
                "q": "What makes an HTTP GET request idempotent?",
                "options": ["Making multiple identical requests produces the exact same server resource state", "It encrypts payloads", "It runs faster than POST", "It triggers server database writes"],
                "correct": "Making multiple identical requests produces the exact same server resource state",
                "explain": "An idempotent method can be called multiple times without altering the server state beyond the initial call."
            }
        ],
        "Cloud & DevOps Engineer": [
            {
                "q": "Which Dockerfile instruction specifies the default executable and arguments when running a container?",
                "options": ["RUN", "CMD / ENTRYPOINT", "ENV", "EXPOSE"],
                "correct": "CMD / ENTRYPOINT",
                "explain": "CMD provides defaults for an executing container, while ENTRYPOINT configures a container that will run as an executable."
            },
            {
                "q": "What does the Principle of Least Privilege dictate in Cloud IAM?",
                "options": ["Users/services should be granted ONLY the minimal permissions required for their tasks", "All root users get admin keys", "Never use passwords", "Store keys in GitHub"],
                "correct": "Users/services should be granted ONLY the minimal permissions required for their tasks",
                "explain": "Least privilege minimizes security blast radius by preventing over-permissioned service accounts."
            }
        ]
    }

    quiz_questions = QUIZ_SETS.get(career, QUIZ_SETS["Data Analyst"])
    last_quiz_result = None

    if request.method == "POST":
        score = 0
        total = len(quiz_questions)
        for i, item in enumerate(quiz_questions):
            ans = request.form.get(f"q_{i}")
            if ans == item["correct"]:
                score += 1
        percentage = round((score / total) * 100) if total else 0
        feedback = f"Outstanding! You demonstrated high conceptual mastery ({score}/{total})." if percentage >= 75 else f"Good effort ({score}/{total}). Review the conceptual breakdowns to reach 100% confidence."
        
        with db() as conn:
            conn.execute("""
            INSERT INTO confidence_tests (workspace, career, score, total, percentage, feedback, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (wid, career, score, total, percentage, feedback, date.today().isoformat()))
        flash(f"Confidence Verification Complete! You scored {score}/{total} ({percentage}%).", "success")
        return redirect(url_for("confidence"))

    with db() as conn:
        last_quiz_result = conn.execute("SELECT * FROM confidence_tests WHERE workspace=? ORDER BY id DESC LIMIT 1", (wid,)).fetchone()

    return render_template(
        "confidence.html",
        career=career,
        confidence=conf,
        quiz_questions=quiz_questions,
        last_quiz=last_quiz_result
    )

@app.route("/intelligence")
def intelligence():
    career = session.get("last_career", "Data Analyst")
    missing = session.get("last_missing", CAREER_SKILLS.get(career, CAREER_SKILLS["Data Analyst"]))
    details = [{
        "skill": s,
        "why": f"{s} is a core requirement in the industry competency matrix for {career}.",
        "action": LEARNING_RESOURCES.get(s, "Practise with a small project.")
    } for s in missing]
    return render_template("intelligence.html", career=career, details=details)

@app.route("/missions", methods=["GET", "POST"])
def missions():
    wid = workspace_id()
    if request.method == "POST":
        mid = request.form.get("mission_id", "")
        answer = request.form.get("answer", "").strip()
        mission = next((m for m in MISSIONS if m["id"] == mid), None)
        if not mission or not answer:
            flash("Choose a mission and enter your attempt.", "error")
        else:
            with db() as conn:
                conn.execute("INSERT OR IGNORE INTO mission_completions(workspace,mission_id,answer,completed_at) VALUES(?,?,?,?)",
                             (wid, mid, answer, date.today().isoformat()))
            flash(f"✦ Mission completed! +{mission['points']} points added. Confidence elevated!", "success")
        return redirect(url_for("missions"))
    with db() as conn:
        completed = {r["mission_id"] for r in conn.execute("SELECT mission_id FROM mission_completions WHERE workspace=?", (wid,))}
    return render_template("missions.html", missions=MISSIONS, completed=completed)

@app.route("/passport", methods=["GET", "POST"])
def passport():
    wid = workspace_id()
    if request.method == "POST":
        kind = request.form.get("kind", "Project")
        title = request.form.get("title", "").strip()
        url = request.form.get("url", "").strip()
        notes = request.form.get("notes", "").strip()
        if kind not in ["Project", "Certificate", "GitHub", "Milestone"] or not title:
            flash("Enter a title and choose a valid evidence type.", "error")
        elif url and not (url.startswith("https://") or url.startswith("http://")):
            flash("Links must begin with http:// or https://.", "error")
        else:
            with db() as conn:
                conn.execute("INSERT INTO passport(workspace,kind,title,url,notes,created_at) VALUES(?,?,?,?,?,?)",
                             (wid, kind, title, url, notes, date.today().isoformat()))
            flash("Evidence stamped in your Skill Passport!", "success")
        return redirect(url_for("passport"))
    with db() as conn:
        items = conn.execute("SELECT * FROM passport WHERE workspace=? ORDER BY id DESC", (wid,)).fetchall()
    return render_template("passport.html", items=items)

@app.route("/sprint", methods=["GET", "POST"])
def sprint():
    wid = workspace_id()
    career = session.get("last_career", "Data Analyst")
    missing = session.get("last_missing", CAREER_SKILLS.get(career, CAREER_SKILLS["Data Analyst"]))
    if request.method == "POST":
        hours = request.form.get("hours", "5")
        try: hours = max(1, min(30, int(hours)))
        except ValueError: hours = 5
        week = date.today().isoformat()
        with db() as conn:
            conn.execute("DELETE FROM sprint_tasks WHERE workspace=? AND week_start=?", (wid, week))
            for skill in missing[:7]:
                conn.execute("INSERT INTO sprint_tasks(workspace,week_start,skill,task) VALUES(?,?,?,?)",
                             (wid, week, skill, LEARNING_RESOURCES.get(skill, "Complete a practical exercise.")))
        flash(f"⚡ Smart sprint generated for {hours} study hours/week.", "success")
        return redirect(url_for("sprint"))
    with db() as conn:
        tasks = conn.execute("SELECT * FROM sprint_tasks WHERE workspace=? ORDER BY id", (wid,)).fetchall()
    return render_template("sprint.html", career=career, missing=missing, tasks=tasks)

@app.post("/sprint/toggle/<int:task_id>")
def toggle_task(task_id):
    with db() as conn:
        conn.execute("UPDATE sprint_tasks SET done=CASE done WHEN 1 THEN 0 ELSE 1 END WHERE id=? AND workspace=?",
                     (task_id, workspace_id()))
    return redirect(url_for("sprint"))

@app.route("/interview", methods=["GET", "POST"])
def interview():
    career = request.values.get("career") or session.get("last_career", "Data Analyst")
    if career not in INTERVIEW_QUESTIONS: career = "Data Analyst"
    questions = INTERVIEW_QUESTIONS[career]
    if request.method == "POST":
        question = request.form.get("question", "")
        answer = request.form.get("answer", "").strip()
        try: rating = int(request.form.get("rating", "3"))
        except ValueError: rating = 3
        rating = max(1, min(5, rating))
        if question not in [q for q, _ in questions] or not answer:
            flash("Select a valid question and write your answer.", "error")
        else:
            with db() as conn:
                conn.execute("INSERT INTO interview_attempts(workspace,career,question,answer,self_rating,created_at) VALUES(?,?,?,?,?,?)",
                             (workspace_id(), career, question, answer, rating, date.today().isoformat()))
            flash(f"Interview response recorded! Self-confidence: {rating}/5 stars.", "success")
        return redirect(url_for("interview", career=career))
    with db() as conn:
        attempts = conn.execute("SELECT * FROM interview_attempts WHERE workspace=? ORDER BY id DESC LIMIT 5", (workspace_id(),)).fetchall()
    return render_template("interview.html", careers=list(INTERVIEW_QUESTIONS), career=career, questions=questions, attempts=attempts)

@app.route("/projects")
def projects():
    career = session.get("last_career", "Data Analyst")
    missing = session.get("last_missing", CAREER_SKILLS.get(career, CAREER_SKILLS["Data Analyst"]))
    ideas = {
        "Python": "Build an Automated ETL script that extracts data from a public API, validates clean schemas, and saves to SQLite.",
        "SQL": "Design an eCommerce star-schema database and author 5 analytical queries with window functions and CTEs.",
        "Statistics": "Conduct an A/B test analysis on conversion rates with hypothesis testing and confidence intervals in Python/Excel.",
        "Data Visualization": "Construct a responsive interactive dashboard using charts that highlight key business metrics and anomalies.",
        "HTML": "Build a responsive, accessible landing page meeting WCAG AA standards with full semantic tagging.",
        "CSS": "Create a responsive component library featuring modern CSS Grid, Flexbox, micro-interactions, and dark mode.",
        "JavaScript": "Engineer a real-time reactive search and filtering application with debouncing, async fetch, and localStorage caching.",
        "React": "Develop an interactive role dashboard with state management hooks, reusable components, and API integration.",
        "Git": "Architect an open-source GitHub repository with automated GitHub Actions CI testing, branch protection, and clear README.",
        "OOP": "Design an object-oriented banking simulation showcasing inheritance, polymorphism, and encapsulation.",
        "Flask": "Build a full-featured CRUD application with SQLite storage, Jinja templating, and REST API endpoints.",
        "Machine Learning": "Train and compare 3 classification algorithms on a Kaggle dataset, reporting ROC-AUC and confusion matrices.",
        "Pandas": "Build an automated data cleaning script that handles missing values, detects outliers with IQR, and generates summaries.",
        "Scikit-learn": "Create an end-to-end ML pipeline with ColumnTransformer, StandardScaler, GridSearchCV tuning, and export.",
        "Excel": "Construct a comprehensive financial model spreadsheet with XLOOKUP, dynamic PivotTables, and scenario managers.",
        "Docker": "Containerize a multi-tier web service with Docker Compose, volume mounts, and health checks.",
        "Linux": "Write a bash automation suite that monitors system disk metrics and rotates server logs.",
        "CI/CD": "Implement an automated GitHub Actions deployment pipeline with linting, unit tests, and Docker build.",
        "TypeScript": "Refactor a vanilla JavaScript application to strictly-typed TypeScript with shared API interfaces.",
        "REST APIs": "Architect an OpenAPI-compliant microservice with token authorization, validation, and rate limits.",
        "Deep Learning": "Train a convolutional neural network on image classification with PyTorch/TensorFlow, tuning dropout and learning rates."
    }
    return render_template("projects.html", career=career, ideas=[(s, ideas.get(s, "Build a portfolio project that demonstrates this skill.")) for s in missing])

@app.route("/growth")
def growth():
    wid = workspace_id()
    conf = calculate_confidence_index(wid)
    with db() as conn:
        completed = conn.execute("SELECT COUNT(*) n FROM mission_completions WHERE workspace=?", (wid,)).fetchone()["n"]
        passport_count = conn.execute("SELECT COUNT(*) n FROM passport WHERE workspace=?", (wid,)).fetchone()["n"]
        sprint_done = conn.execute("SELECT COUNT(*) n FROM sprint_tasks WHERE workspace=? AND done=1", (wid,)).fetchone()["n"]
        sprint_total = conn.execute("SELECT COUNT(*) n FROM sprint_tasks WHERE workspace=?", (wid,)).fetchone()["n"]
        interview_count = conn.execute("SELECT COUNT(*) n FROM interview_attempts WHERE workspace=?", (wid,)).fetchone()["n"]
        doubts_cleared = conn.execute("SELECT COUNT(*) n FROM doubts WHERE workspace=? AND is_cleared=1", (wid,)).fetchone()["n"]
    return render_template(
        "growth.html",
        completed=completed,
        passport_count=passport_count,
        sprint_done=sprint_done,
        sprint_total=sprint_total,
        interview_count=interview_count,
        doubts_cleared=doubts_cleared,
        confidence=conf,
        points=get_points()
    )

@app.route("/health")
def health():
    return {"status": "ok", "application": "SkillBridge AI", "database": "sqlite", "version": "3.0-google-insta-edition"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
