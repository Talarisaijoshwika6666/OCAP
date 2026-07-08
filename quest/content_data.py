"""
Educational content for Quest > Learning Path > Topic pages.

Structure
---------
BASIC_SECTIONS / INTERMEDIATE_SECTIONS define the ordered list of section
blocks shown on the Basic and Intermediate tabs of a topic page (key, title,
icon). TOPIC_CONTENT maps a topic slug (matching `slugify(topic['title'])`
from LEARNING_PATHS in views.py) to the actual HTML content for each
section key, split into "basic" and "intermediate" dictionaries.

Content is written as small, safe HTML fragments (paragraphs, lists, and
code blocks) so it can be rendered directly inside the existing
`quest/includes/topic_section.html` card without touching layout, styling,
or routing.
"""

BASIC_SECTIONS = [
    {"key": "introduction", "title": "Introduction", "icon": "fas fa-door-open"},
    {"key": "why_it_matters", "title": "Why It Matters", "icon": "fas fa-star"},
    {"key": "core_concepts", "title": "Core Concepts", "icon": "fas fa-lightbulb"},
    {"key": "simple_examples", "title": "Simple Examples", "icon": "fas fa-code"},
    {"key": "important_notes", "title": "Important Notes", "icon": "fas fa-circle-info"},
    {"key": "common_mistakes", "title": "Common Mistakes", "icon": "fas fa-triangle-exclamation"},
    {"key": "summary", "title": "Summary", "icon": "fas fa-flag-checkered"},
]

INTERMEDIATE_SECTIONS = [
    {"key": "advanced_concepts", "title": "Advanced Concepts", "icon": "fas fa-brain"},
    {"key": "time_complexity", "title": "Time Complexity", "icon": "fas fa-stopwatch"},
    {"key": "space_complexity", "title": "Space Complexity", "icon": "fas fa-memory"},
    {"key": "interview_questions", "title": "Interview Questions", "icon": "fas fa-comments"},
    {"key": "real_world_applications", "title": "Real-World Applications", "icon": "fas fa-globe"},
    {"key": "practice_tips", "title": "Practice Tips", "icon": "fas fa-dumbbell"},
]


TOPIC_CONTENT = {}

# ============================================================================
# DATA STRUCTURES — Arrays & Strings
# ============================================================================
TOPIC_CONTENT["arrays-strings"] = {
    "basic": {
        "introduction": """
<p>An <strong>array</strong> is a collection of elements stored in contiguous
memory, each one reachable by an index. A <strong>string</strong> is, at its
core, an array of characters with a few extra conveniences layered on top by
whatever language you're using. Together they are the very first data
structures most programmers meet, and almost every other structure you will
learn — lists, stacks, queues, hash tables — is either built on top of an
array or inspired by the way arrays organize memory.</p>
<p>Because indexing is direct, arrays let you jump straight to any element
without walking through the ones before it. That single property — instant
access by position — is what makes arrays the default choice whenever you
need to store an ordered collection of things.</p>
""",
        "why_it_matters": """
<p>Arrays and strings show up constantly, in both interviews and real
software:</p>
<ul>
<li><strong>Predictable performance.</strong> Reading any element by index
takes the same amount of time whether it's the 1st or the 1,000,000th.</li>
<li><strong>Foundation for other structures.</strong> Dynamic arrays,
matrices, hash tables, and even parts of trees and heaps are implemented
using arrays under the hood.</li>
<li><strong>Interview frequency.</strong> A large share of coding interview
questions — two pointers, sliding window, sorting, searching — are really
array and string problems in disguise.</li>
<li><strong>Text is everywhere.</strong> Parsing input, validating data,
formatting output, and processing user text all rely on solid string
handling.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Indexing.</strong> Elements are numbered starting from 0 in most
languages. <code>arr[0]</code> is the first element, <code>arr[arr.length -
1]</code> is the last.</p>
<p><strong>Fixed-size vs. dynamic arrays.</strong> A traditional array has a
fixed capacity set at creation time. Dynamic arrays (like Python's
<code>list</code>, Java's <code>ArrayList</code>, or C++'s
<code>vector</code>) grow automatically by allocating a larger block of
memory and copying elements over when they run out of room.</p>
<p><strong>Contiguous memory.</strong> Because elements sit next to each
other in memory, the computer can calculate the address of any element with
simple arithmetic — this is what makes constant-time access possible.</p>
<p><strong>Strings as arrays.</strong> A string is usually a sequence of
character codes. Many languages make strings <em>immutable</em>, meaning
every "modification" (like concatenation) actually creates a brand-new
string rather than changing the original in place.</p>
<p><strong>Common operations.</strong> Traversal (visiting every element),
insertion, deletion, searching, and slicing (extracting a sub-range) form the
toolkit you'll reuse in almost every array or string problem.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — Traversing an array:</strong></p>
<pre><code>numbers = [4, 8, 15, 16, 23, 42]
total = 0
for n in numbers:
    total += n
print(total)  # 108
</code></pre>
<p><strong>Example 2 — Accessing and updating by index:</strong></p>
<pre><code>fruits = ["apple", "banana", "cherry"]
print(fruits[1])      # banana
fruits[1] = "mango"
print(fruits)          # ["apple", "mango", "cherry"]
</code></pre>
<p><strong>Example 3 — Reversing a string:</strong></p>
<pre><code>word = "quest"
reversed_word = word[::-1]
print(reversed_word)   # tseuq
</code></pre>
<p><strong>Example 4 — Checking for a substring:</strong></p>
<pre><code>sentence = "learning data structures"
print("data" in sentence)   # True
</code></pre>
""",
        "important_notes": """
<ul>
<li>Array indices start at <strong>0</strong>, not 1 — this trips up almost
every beginner at least once.</li>
<li>Accessing an index that doesn't exist raises an error
(<code>IndexError</code> in Python, <code>ArrayIndexOutOfBoundsException</code>
in Java) — always check bounds when the index comes from a calculation.</li>
<li>Strings are usually immutable. Repeatedly concatenating strings in a loop
can be surprisingly slow because each concatenation may create a new string
in memory.</li>
<li>Inserting or deleting from the <em>middle</em> of an array requires
shifting every element after it — this is more expensive than it looks.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Off-by-one errors</strong> — looping one step too far or too
short, especially with <code>&lt;=</code> vs <code>&lt;</code> in loop
conditions.</li>
<li><strong>Assuming insertion is free.</strong> Inserting at the front of an
array is far more expensive than appending at the end, since everything else
must shift over.</li>
<li><strong>Mutating while iterating.</strong> Removing elements from an
array while looping over it can skip elements or cause index errors.</li>
<li><strong>Confusing shallow copies with deep copies</strong> — copying a
reference to an array, rather than its contents, means changes to the "copy"
affect the original too.</li>
</ul>
""",
        "summary": """
<p>Arrays store elements in order, in contiguous memory, and give you instant
access by index. Strings behave like arrays of characters but are usually
immutable. Mastering traversal, indexing, and the cost of insertion/deletion
gives you the foundation you need before moving into more advanced
structures like linked lists and trees. Almost every interview problem
involving "find," "reverse," "sort," or "count" on a sequence starts with
these fundamentals.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Two pointers.</strong> Many array problems become efficient when
you use two index variables that move toward each other or in the same
direction — for example, checking if a string is a palindrome by comparing
characters from both ends inward.</p>
<p><strong>Sliding window.</strong> A window defined by two pointers expands
and contracts over a subarray or substring to track a running sum, count, or
set of characters, avoiding the need to recompute from scratch at each step.</p>
<p><strong>Prefix sums.</strong> Precomputing cumulative sums lets you answer
"sum of elements between index i and j" queries in constant time after an
initial linear pass.</p>
<p><strong>In-place manipulation.</strong> Techniques like the Dutch National
Flag algorithm or in-place array rotation let you transform an array without
allocating extra memory, which matters when space is constrained.</p>
<p><strong>String matching.</strong> Algorithms such as KMP (Knuth-Morris-Pratt)
find a pattern inside a larger string in linear time by avoiding redundant
re-comparisons, unlike the naive approach which can be quadratic.</p>
""",
        "time_complexity": """
<ul>
<li><strong>Access by index:</strong> O(1) — direct memory calculation.</li>
<li><strong>Search (unsorted):</strong> O(n) — must check each element in
the worst case.</li>
<li><strong>Search (sorted, binary search):</strong> O(log n).</li>
<li><strong>Insertion/deletion at the end:</strong> O(1) amortized for
dynamic arrays.</li>
<li><strong>Insertion/deletion at the start or middle:</strong> O(n) —
requires shifting elements.</li>
<li><strong>String concatenation in a loop:</strong> O(n²) in languages with
immutable strings, unless you use a builder/buffer structure, which brings
it down to O(n).</li>
</ul>
""",
        "space_complexity": """
<p>A standard array or string uses O(n) space, proportional to the number of
elements it holds. Watch for hidden space costs in otherwise "in-place"
looking solutions:</p>
<ul>
<li>Slicing a string or array (e.g. <code>arr[1:5]</code>) often creates a
new copy, adding O(k) space for a slice of length k.</li>
<li>Recursive solutions on arrays (like recursive reversal) use O(n) stack
space even if no extra array is allocated.</li>
<li>True in-place algorithms — swapping elements using a couple of temporary
variables — achieve O(1) extra space, which interviewers often explicitly
ask for.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>Given an array, find two numbers that add up to a target value (Two Sum).</li>
<li>Determine whether a string is a valid palindrome, ignoring
non-alphanumeric characters and case.</li>
<li>Find the maximum sum of any contiguous subarray (Kadane's Algorithm).</li>
<li>Rotate an array to the right by k steps, in place.</li>
<li>Given two strings, determine if one is an anagram of the other.</li>
<li>Find the longest substring without repeating characters.</li>
<li>Merge two sorted arrays into one sorted array without using extra
space beyond what's given.</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>Search engines</strong> use string-matching algorithms to index
and find text across billions of documents.</li>
<li><strong>Spreadsheets and databases</strong> store rows as arrays of
values internally, enabling fast row-by-index lookups.</li>
<li><strong>Compilers and interpreters</strong> tokenize source code by
scanning strings character by character.</li>
<li><strong>Image processing</strong> represents pixels as 2D arrays, where
each cell holds color data that can be transformed with array operations.</li>
<li><strong>Autocomplete and spell-check</strong> features rely on efficient
substring and prefix matching over large word lists.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Before coding, restate the problem and ask about edge cases: empty
array, single element, duplicates, or negative numbers.</li>
<li>Draw the array on paper (or a whiteboard) and simulate pointer movement
by hand — most two-pointer and sliding-window bugs are caught this way.</li>
<li>Practice converting a brute-force O(n²) solution into an O(n) one using
a hash set, prefix sum, or two-pointer technique; this is the single most
common interview pattern.</li>
<li>Time yourself solving 2-3 array/string problems per session and review
the optimal solution afterward, even if yours passed.</li>
</ul>
""",
    },
}

# ============================================================================
# DATA STRUCTURES — Linked Lists
# ============================================================================
TOPIC_CONTENT["linked-lists"] = {
    "basic": {
        "introduction": """
<p>A <strong>linked list</strong> is a chain of nodes, where each node holds
a value and a reference (a "pointer" or "link") to the next node in the
sequence. Unlike an array, the nodes are not necessarily stored next to each
other in memory — they can live anywhere, connected only by these
references. The list itself just remembers where the chain begins (the
<em>head</em>), and sometimes where it ends (the <em>tail</em>).</p>
<p>This simple idea — "a value plus a pointer to the next thing" — gives
linked lists a completely different set of strengths and weaknesses compared
to arrays, which is exactly why both structures exist side by side.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Flexible size.</strong> A linked list can grow or shrink one
node at a time without ever needing to "resize" or copy existing data.</li>
<li><strong>Cheap insertion/deletion.</strong> Adding or removing a node at
the front (or anywhere you already have a reference to) doesn't require
shifting other elements, unlike an array.</li>
<li><strong>Building block for other structures.</strong> Stacks, queues,
and hash table buckets are frequently implemented with linked lists under
the hood.</li>
<li><strong>Conceptual stepping stone.</strong> Linked lists are usually the
first place students learn to reason about pointers/references — a skill
that carries directly into trees and graphs.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Node.</strong> The basic unit of a linked list, holding a value
and a reference to the next node (and, in a doubly linked list, a reference
to the previous node too).</p>
<p><strong>Head and tail.</strong> The head is the first node in the list;
the tail is the last one, whose "next" reference points to nothing
(<code>null</code>/<code>None</code>).</p>
<p><strong>Singly vs. doubly linked lists.</strong> A singly linked list only
lets you move forward, node by node. A doubly linked list adds a "previous"
pointer, allowing traversal in both directions at the cost of extra memory
per node.</p>
<p><strong>No random access.</strong> To reach the 5th node, you must walk
through the first four — there's no way to "jump" directly like
<code>arr[4]</code> in an array.</p>
<p><strong>Circular linked lists.</strong> A variant where the tail points
back to the head instead of to <code>null</code>, useful for round-robin
style processing.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — Defining a node:</strong></p>
<pre><code>class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
</code></pre>
<p><strong>Example 2 — Building a small list manually:</strong></p>
<pre><code>head = Node(10)
head.next = Node(20)
head.next.next = Node(30)
# 10 -&gt; 20 -&gt; 30 -&gt; None
</code></pre>
<p><strong>Example 3 — Traversing and printing every value:</strong></p>
<pre><code>current = head
while current is not None:
    print(current.value)
    current = current.next
</code></pre>
<p><strong>Example 4 — Inserting a new node at the front:</strong></p>
<pre><code>new_node = Node(5)
new_node.next = head
head = new_node
# 5 -&gt; 10 -&gt; 20 -&gt; 30 -&gt; None
</code></pre>
""",
        "important_notes": """
<ul>
<li>Always keep a reference to the <strong>head</strong> — lose it, and you
lose access to the entire list.</li>
<li>When deleting a node, you must update the <em>previous</em> node's
<code>next</code> pointer to skip over it; forgetting this leaves the list
unchanged or broken.</li>
<li>The last node's <code>next</code> should always point to
<code>None</code>/<code>null</code> — forgetting to set this can cause
infinite loops during traversal.</li>
<li>Linked lists use extra memory per element to store the pointer(s),
compared to a plain array.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Losing the head reference</strong> while traversing, by
reassigning the head variable instead of a temporary "current" variable.</li>
<li><strong>Forgetting to update both directions</strong> in a doubly linked
list, leaving <code>next</code> and <code>previous</code> pointers out of
sync.</li>
<li><strong>Off-by-one errors</strong> when trying to insert "before" a
given node, since you typically need a reference to the node <em>before</em>
the target.</li>
<li><strong>Creating a cycle by accident</strong> — pointing a node's
<code>next</code> back to an earlier node, which causes infinite loops.</li>
</ul>
""",
        "summary": """
<p>Linked lists trade the instant indexed access of arrays for flexible,
low-cost insertion and deletion. Each node stores a value and a pointer to
the next node, and the list is only as accessible as its head reference
allows. Understanding how to safely traverse, insert, and delete nodes by
carefully managing pointers is the core skill this topic builds — and it
directly prepares you for trees, which are really just linked lists with
more than one "next" pointer per node.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Reversing a linked list.</strong> By iterating through the list
and flipping each node's <code>next</code> pointer to point backward instead
of forward, you can reverse the entire list in a single pass without extra
memory.</p>
<p><strong>Cycle detection (Floyd's algorithm).</strong> Using two pointers
— a "slow" one moving one step at a time and a "fast" one moving two steps
— you can detect whether a list loops back on itself; if the fast pointer
ever catches the slow one, a cycle exists.</p>
<p><strong>Finding the middle node.</strong> The same slow/fast pointer
technique finds the middle of a list in one pass: when the fast pointer
reaches the end, the slow pointer is at the midpoint.</p>
<p><strong>Merging sorted lists.</strong> Two sorted linked lists can be
merged into one sorted list by repeatedly comparing the front nodes of each
and re-linking pointers, without allocating a new array.</p>
<p><strong>Dummy/sentinel nodes.</strong> Adding a placeholder node before
the real head simplifies edge cases (like deleting the head itself) because
every real node then has a consistent "previous" node to update.</p>
""",
        "time_complexity": """
<ul>
<li><strong>Access by position:</strong> O(n) — must traverse from the head.</li>
<li><strong>Search for a value:</strong> O(n).</li>
<li><strong>Insertion/deletion at the head:</strong> O(1).</li>
<li><strong>Insertion/deletion at the tail:</strong> O(1) if a tail pointer
is maintained, otherwise O(n).</li>
<li><strong>Insertion/deletion given a reference to the node:</strong> O(1)
for singly linked lists when inserting after; O(1) for doubly linked lists
in either direction.</li>
<li><strong>Reversal or cycle detection:</strong> O(n) time.</li>
</ul>
""",
        "space_complexity": """
<p>A linked list of n elements uses O(n) space for the nodes themselves,
plus O(1) extra per node for the pointer(s) — this overhead is the main
trade-off compared to arrays. Most linked list algorithms (reversal, cycle
detection, merging) can be done <strong>iteratively</strong> in O(1) extra
space. Recursive implementations of the same algorithms use O(n) additional
space for the call stack, which is worth mentioning explicitly if an
interviewer asks you to optimize space.</p>
""",
        "interview_questions": """
<ul>
<li>Reverse a singly linked list, both iteratively and recursively.</li>
<li>Detect whether a linked list contains a cycle, and find where it
begins.</li>
<li>Find the middle node of a linked list in a single traversal.</li>
<li>Merge two sorted linked lists into one sorted list.</li>
<li>Remove the nth node from the end of a list in one pass.</li>
<li>Check whether a linked list is a palindrome.</li>
<li>Flatten a multilevel linked list (nodes with both "next" and "child"
pointers).</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>Undo/redo history</strong> in text editors and design tools,
where each action links to the previous and next state.</li>
<li><strong>Music and video playlists</strong>, where "next" and "previous"
track navigation maps directly onto a doubly linked list.</li>
<li><strong>Browser history</strong> (back/forward navigation) is a classic
real-world doubly linked list.</li>
<li><strong>Memory allocators</strong> use linked lists to track free blocks
of memory that can be reused.</li>
<li><strong>Operating system schedulers</strong> often use circular linked
lists to cycle through processes in round-robin fashion.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Draw the list as boxes and arrows on paper before writing code — pointer
manipulation bugs are much easier to spot visually.</li>
<li>Practice the "dummy node" pattern until it's automatic; it removes a
huge class of head-related edge-case bugs.</li>
<li>Get comfortable with the slow/fast pointer technique — it solves middle
node, cycle detection, and "nth from the end" problems with the same core
idea.</li>
<li>After solving a problem recursively, redo it iteratively (and vice
versa) to build fluency with both approaches, since interviewers often ask
for both.</li>
</ul>
""",
    },
}

# ============================================================================
# DATA STRUCTURES — Trees & Graphs
# ============================================================================
TOPIC_CONTENT["trees-graphs"] = {
    "basic": {
        "introduction": """
<p>A <strong>tree</strong> is a way of organizing data into a hierarchy: one
node sits at the top (the <em>root</em>), and every other node has exactly
one parent, forming branches that fan outward. A <strong>graph</strong> is a
more general structure — a set of nodes (often called <em>vertices</em>)
connected by links (<em>edges</em>), with no requirement that it forms a
neat hierarchy. In fact, every tree is a special kind of graph: one with no
cycles and exactly one path between any two nodes.</p>
<p>These structures model relationships rather than plain sequences — think
folders inside folders, friends connected to friends, or cities linked by
roads — which is why they show up whenever data has structure beyond "first,
second, third."</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Hierarchies are everywhere.</strong> File systems, organization
charts, HTML/DOM structure, and decision trees are all naturally modeled as
trees.</li>
<li><strong>Networks are everywhere.</strong> Social networks, maps, the
internet's routing structure, and recommendation systems are all graphs.</li>
<li><strong>Efficient searching and sorting.</strong> Balanced trees (like
binary search trees) keep search, insert, and delete operations fast even as
data grows.</li>
<li><strong>Heavily tested in interviews.</strong> Tree and graph traversal
problems are among the most common categories asked at every experience
level.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Tree terminology.</strong> The <em>root</em> is the top node;
<em>children</em> are nodes directly below a given node; a <em>leaf</em> has
no children; the <em>height</em> of a tree is the length of the longest path
from root to leaf.</p>
<p><strong>Binary trees.</strong> Each node has at most two children,
typically called <em>left</em> and <em>right</em>. A <strong>binary search
tree (BST)</strong> additionally keeps all values in the left subtree
smaller than the node, and all values in the right subtree larger.</p>
<p><strong>Tree traversal.</strong> <em>Pre-order</em> (node, then left, then
right), <em>in-order</em> (left, node, right — gives sorted order in a BST),
<em>post-order</em> (left, right, node), and <em>level-order</em> (breadth
by breadth, using a queue) are the standard ways to visit every node.</p>
<p><strong>Graph terminology.</strong> A graph can be <em>directed</em>
(edges have a direction, like a one-way street) or <em>undirected</em>
(edges go both ways), and <em>weighted</em> (edges carry a cost) or
<em>unweighted</em>.</p>
<p><strong>Graph representation.</strong> An <em>adjacency list</em> stores,
for each node, a list of its neighbors — compact and common in practice. An
<em>adjacency matrix</em> stores a grid marking which pairs of nodes are
connected — simple but uses more memory for sparse graphs.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — A simple binary tree node:</strong></p>
<pre><code>class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

root = TreeNode(10)
root.left = TreeNode(5)
root.right = TreeNode(15)
</code></pre>
<p><strong>Example 2 — In-order traversal of a BST:</strong></p>
<pre><code>def in_order(node):
    if node is None:
        return
    in_order(node.left)
    print(node.value)
    in_order(node.right)
# Output for the tree above: 5, 10, 15
</code></pre>
<p><strong>Example 3 — Representing a graph as an adjacency list:</strong></p>
<pre><code>graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A"],
    "D": ["B"],
}
</code></pre>
<p><strong>Example 4 — Breadth-first search (BFS) on that graph:</strong></p>
<pre><code>from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order
# bfs(graph, "A") -&gt; ["A", "B", "C", "D"]
</code></pre>
""",
        "important_notes": """
<ul>
<li>A tree has exactly <strong>n - 1 edges</strong> for n nodes and contains
no cycles — if you ever find a cycle, it's a graph, not a tree.</li>
<li>Always mark nodes as <strong>visited</strong> when traversing a graph;
without this, cycles cause infinite loops.</li>
<li>In-order traversal only produces sorted output for a <strong>binary
search tree</strong> — it does not sort an arbitrary binary tree.</li>
<li>A binary search tree that isn't kept balanced can degrade into a
straight line, losing its performance advantage entirely.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Forgetting the visited set</strong> in graph traversal, causing
infinite loops on cyclic graphs.</li>
<li><strong>Mixing up traversal orders</strong> (pre/in/post-order) and their
use cases, especially under interview pressure.</li>
<li><strong>Assuming a tree is balanced</strong> when analyzing time
complexity — a skewed tree behaves like a linked list, not like a balanced
structure.</li>
<li><strong>Confusing directed and undirected edges</strong> when building an
adjacency list, forgetting to add the edge in both directions for undirected
graphs.</li>
</ul>
""",
        "summary": """
<p>Trees model hierarchy; graphs model general networks of relationships,
with trees being a special, cycle-free case of graphs. Traversal — visiting
every node in a systematic order — is the core skill for both, whether
that's depth-first (pre/in/post-order, or plain DFS) or breadth-first (level
by level, using a queue). Once traversal feels natural, most tree and graph
problems become variations on "visit every node, and do something useful
along the way."</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Balanced trees.</strong> Structures like AVL trees and red-black
trees automatically rebalance themselves after insertions and deletions,
guaranteeing O(log n) height regardless of insertion order — this is what
powers many language libraries' sorted map/set implementations.</p>
<p><strong>Depth-first search (DFS) vs. breadth-first search (BFS).</strong>
DFS explores as far as possible down one branch before backtracking (often
implemented recursively or with a stack); BFS explores level by level using
a queue. The choice affects both which problems they solve naturally
(shortest path in an unweighted graph favors BFS) and their memory profile.</p>
<p><strong>Shortest path algorithms.</strong> Dijkstra's algorithm finds the
shortest path in a weighted graph with non-negative edges; Bellman-Ford
handles negative weights; both build on the same graph traversal
fundamentals with a priority queue or relaxation step added.</p>
<p><strong>Topological sort.</strong> For a directed acyclic graph (DAG),
this orders nodes so that every edge points from an earlier node to a later
one — essential for scheduling tasks with dependencies.</p>
<p><strong>Union-Find (Disjoint Set).</strong> A structure for efficiently
tracking which nodes belong to the same connected component, widely used in
graph algorithms like Kruskal's minimum spanning tree.</p>
""",
        "time_complexity": """
<ul>
<li><strong>BST search/insert/delete (balanced):</strong> O(log n).</li>
<li><strong>BST search/insert/delete (unbalanced, worst case):</strong>
O(n).</li>
<li><strong>Tree traversal (any order):</strong> O(n) — every node is
visited once.</li>
<li><strong>Graph BFS/DFS:</strong> O(V + E), where V is the number of
vertices and E is the number of edges.</li>
<li><strong>Dijkstra's algorithm (with a min-heap):</strong> O((V + E) log
V).</li>
<li><strong>Topological sort:</strong> O(V + E).</li>
</ul>
""",
        "space_complexity": """
<p>Storing a tree or graph itself takes O(n) or O(V + E) space respectively.
Traversal algorithms add their own overhead on top:</p>
<ul>
<li>Recursive DFS uses O(h) additional space for the call stack, where h is
the tree's height — O(log n) for a balanced tree, but O(n) for a skewed
one.</li>
<li>BFS uses O(w) space for the queue, where w is the maximum "width" of the
tree or graph at any level.</li>
<li>An adjacency matrix uses O(V²) space regardless of how many edges
actually exist, which is wasteful for sparse graphs — an adjacency list
uses O(V + E) instead.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>Check whether a binary tree is a valid binary search tree.</li>
<li>Find the lowest common ancestor of two nodes in a binary tree.</li>
<li>Determine the maximum depth (height) of a binary tree.</li>
<li>Detect a cycle in a directed graph.</li>
<li>Count the number of connected components in an undirected graph.</li>
<li>Find the shortest path between two nodes in an unweighted graph using
BFS.</li>
<li>Serialize and deserialize a binary tree to and from a string.</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>File systems</strong> are literal trees — folders containing
folders and files.</li>
<li><strong>GPS and mapping applications</strong> model roads as a weighted
graph and use shortest-path algorithms to find directions.</li>
<li><strong>Social networks</strong> represent people as nodes and
friendships/follows as edges, using graph algorithms to suggest connections.</li>
<li><strong>Compilers</strong> represent source code as an abstract syntax
tree (AST) to analyze and generate machine code.</li>
<li><strong>Build systems and task schedulers</strong> use topological sort
to determine a valid order for tasks with dependencies.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Master the recursive template for tree problems first — most solutions
follow the same shape: handle the base case, recurse on children, combine
results.</li>
<li>Practice converting a recursive DFS into an iterative one using an
explicit stack; interviewers sometimes ask for both.</li>
<li>When a graph problem feels hard, explicitly identify whether it's really
asking for BFS (shortest path/levels), DFS (exploring all paths/detecting
cycles), or a shortest-path algorithm — naming the right tool cuts the
problem down to size.</li>
<li>Draw the tree or graph before coding. Trace your algorithm on the
drawing by hand for at least one example before writing any code.</li>
</ul>
""",
    },
}

# ============================================================================
# DATA STRUCTURES — Dynamic Programming
# ============================================================================
TOPIC_CONTENT["dynamic-programming"] = {
    "basic": {
        "introduction": """
<p><strong>Dynamic programming (DP)</strong> is a technique for solving
problems by breaking them into smaller overlapping subproblems, solving each
subproblem only once, and reusing the stored result whenever it's needed
again. The name sounds intimidating, but the core idea is simple: don't
redo work you've already done.</p>
<p>DP applies to problems that have two properties: <em>overlapping
subproblems</em> (the same smaller calculation is needed many times) and
<em>optimal substructure</em> (the best solution to the whole problem can be
built from the best solutions to its pieces). When both are true, DP turns
solutions that would otherwise take exponential time into ones that run in
polynomial time.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Massive performance gains.</strong> DP routinely turns
exponential-time brute-force solutions into linear or polynomial-time ones.</li>
<li><strong>Extremely common in interviews.</strong> DP is considered one of
the harder but most frequently tested topics at mid-to-senior interview
levels.</li>
<li><strong>Trains problem decomposition.</strong> Learning to spot
overlapping subproblems sharpens how you break down any complex problem,
not just DP ones.</li>
<li><strong>Powers real optimization systems</strong> — from route planning
to resource allocation to bioinformatics sequence alignment.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Memoization (top-down).</strong> Write the natural recursive
solution, but store ("memoize") the result of each subproblem the first time
it's computed, and return the cached result instead of recomputing it on
future calls.</p>
<p><strong>Tabulation (bottom-up).</strong> Build a table of solutions to
small subproblems first, then use those to compute larger ones, working
upward until the original problem is solved — no recursion needed.</p>
<p><strong>State.</strong> The "state" of a DP problem is the minimal set of
parameters needed to describe a subproblem — for example, "the maximum
value achievable using the first i items with capacity w remaining" in the
knapsack problem.</p>
<p><strong>Transition (recurrence relation).</strong> The rule that
describes how to compute a state's answer from the answers to smaller
states — this is the heart of any DP solution.</p>
<p><strong>Base case.</strong> The smallest subproblem(s), simple enough to
answer directly without further breakdown — every DP solution needs at
least one.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — Fibonacci, naive recursion (slow):</strong></p>
<pre><code>def fib(n):
    if n &lt;= 1:
        return n
    return fib(n - 1) + fib(n - 2)
# fib(35) recomputes the same subproblems millions of times
</code></pre>
<p><strong>Example 2 — Fibonacci with memoization (fast):</strong></p>
<pre><code>def fib_memo(n, cache={}):
    if n &lt;= 1:
        return n
    if n in cache:
        return cache[n]
    cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]
</code></pre>
<p><strong>Example 3 — Fibonacci with tabulation (bottom-up):</strong></p>
<pre><code>def fib_table(n):
    table = [0, 1]
    for i in range(2, n + 1):
        table.append(table[i - 1] + table[i - 2])
    return table[n]
</code></pre>
<p><strong>Example 4 — Climbing stairs (1 or 2 steps at a time):</strong></p>
<pre><code>def climb_stairs(n):
    if n &lt;= 2:
        return n
    prev, curr = 1, 2
    for _ in range(3, n + 1):
        prev, curr = curr, prev + curr
    return curr
</code></pre>
""",
        "important_notes": """
<ul>
<li>Not every recursive problem needs DP — DP only helps when subproblems
genuinely <strong>overlap</strong>. If every subproblem is unique, memoizing
gains you nothing.</li>
<li>Always identify the <strong>state</strong> and the <strong>transition</strong>
before writing code — most DP mistakes come from skipping this step and
guessing at the code directly.</li>
<li>Bottom-up (tabulation) avoids recursion overhead and stack limits;
top-down (memoization) is often easier to write first and reason about.</li>
<li>Many DP solutions can be optimized to use O(1) or O(n) space instead of a
full 2D table, once you notice you only ever need the last one or two rows.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Writing the recursive solution but forgetting to cache
results</strong> — this looks like DP but performs no better than plain
recursion.</li>
<li><strong>Misidentifying the state</strong> — leaving out a parameter that
actually affects the answer, causing incorrect results.</li>
<li><strong>Off-by-one errors</strong> in table indices, especially when
mapping "the first i items" to a 0-indexed array.</li>
<li><strong>Jumping straight to code</strong> without first writing the
recurrence relation on paper — DP bugs are much harder to fix after the fact
than to prevent up front.</li>
</ul>
""",
        "summary": """
<p>Dynamic programming solves problems by caching the answers to overlapping
subproblems, either top-down with memoization or bottom-up with tabulation.
The real skill isn't the code — it's identifying the state and writing the
recurrence relation that connects a problem to its smaller versions of
itself. Once you can consistently spot overlapping subproblems and optimal
substructure, DP transforms from an intimidating topic into a reliable,
repeatable pattern.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>1D vs. 2D vs. multi-dimensional DP.</strong> Simple problems (like
Fibonacci) need only a 1D array of past results. More complex problems (like
edit distance between two strings) need a 2D table indexed by positions in
both inputs. Some problems require additional dimensions to track extra
state, like "the maximum profit with at most k transactions."</p>
<p><strong>Space optimization.</strong> Because many DP transitions only
depend on the previous row (or a small window of previous states), you can
often reduce a 2D table to a rolling 1D array, cutting space from O(n·m) to
O(m) or even O(1).</p>
<p><strong>Knapsack family.</strong> The 0/1 knapsack (each item used at most
once) and unbounded knapsack (items can be reused) are template problems
that generalize to coin change, subset sum, and partition problems.</p>
<p><strong>Interval DP.</strong> Problems like matrix chain multiplication or
palindrome partitioning define subproblems over ranges [i, j] of the input,
solved by combining smaller sub-ranges.</p>
<p><strong>DP on trees and graphs.</strong> DP isn't limited to sequences —
"maximum independent set in a tree" or "longest path in a DAG" apply the
same overlapping-subproblem idea to hierarchical or graph-shaped inputs.</p>
""",
        "time_complexity": """
<ul>
<li><strong>1D DP (e.g. Fibonacci, climbing stairs):</strong> O(n) time.</li>
<li><strong>2D DP (e.g. edit distance, longest common subsequence):</strong>
O(n·m), where n and m are the lengths of the two inputs.</li>
<li><strong>0/1 Knapsack:</strong> O(n·W), where n is the number of items and
W is the capacity.</li>
<li><strong>Interval DP (e.g. matrix chain multiplication):</strong> O(n³) in
typical formulations.</li>
<li>Compare this to the naive recursive solution for the same problems,
which is frequently exponential — O(2ⁿ) — making DP's polynomial time a
dramatic improvement.</li>
</ul>
""",
        "space_complexity": """
<p>A naive tabulation solution uses space proportional to the size of the DP
table — O(n) for 1D problems, O(n·m) for 2D problems. This is frequently
reducible:</p>
<ul>
<li>If each row only depends on the previous row, you can keep just two rows
in memory, reducing O(n·m) to O(m).</li>
<li>If only the last one or two values matter (as in Fibonacci), you can
reduce an entire array down to O(1) extra space using a couple of
variables.</li>
<li>Recursive/memoized solutions add O(n) (or more) stack space on top of
the cache itself, which is worth mentioning when comparing top-down and
bottom-up approaches in an interview.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>Compute the minimum number of coins needed to make a given amount
(Coin Change).</li>
<li>Find the length of the longest common subsequence between two strings.</li>
<li>Solve the 0/1 knapsack problem: maximize value within a weight limit.</li>
<li>Find the minimum edit distance (insertions, deletions, substitutions)
between two strings.</li>
<li>Determine the maximum profit from at most two stock transactions.</li>
<li>Count the number of distinct ways to partition a string into
palindromic substrings.</li>
<li>Find the length of the longest increasing subsequence in an array.</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>Spell-checkers and DNA sequence alignment</strong> both use edit
distance (a classic 2D DP problem) to measure similarity between
sequences.</li>
<li><strong>Resource allocation and budgeting tools</strong> use
knapsack-style DP to maximize value under a constraint.</li>
<li><strong>Route planning</strong> in logistics uses DP-based approaches to
minimize cost or time across multiple stops.</li>
<li><strong>Compilers</strong> use DP for optimal instruction selection and
register allocation.</li>
<li><strong>Version control systems</strong> (like Git's diff algorithm) rely
on longest-common-subsequence style DP to show what changed between file
versions.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Always start by writing the brute-force recursive solution first, then
identify which subproblems repeat — this makes the transition to memoization
natural rather than mysterious.</li>
<li>Explicitly write out the recurrence relation in words or math notation
before touching code: "answer(i) depends on answer(i-1) and answer(i-2)
because…"</li>
<li>Practice recognizing DP "shapes" — sequence DP, grid DP, knapsack-style,
interval DP — since most interview problems are variations on a handful of
templates.</li>
<li>After getting a working tabulation solution, practice optimizing its
space complexity; interviewers often ask this as a natural follow-up.</li>
</ul>
""",
    },
}

# ============================================================================
# DATABASE — SQL Basics
# ============================================================================
TOPIC_CONTENT["sql-basics"] = {
    "basic": {
        "introduction": """
<p><strong>SQL (Structured Query Language)</strong> is the standard language
used to communicate with relational databases — asking them to store,
retrieve, update, and delete data. Instead of writing custom code to search
through files, you describe <em>what</em> data you want, and the database
figures out <em>how</em> to get it.</p>
<p>Data in a relational database is organized into <strong>tables</strong>,
each made of rows (individual records) and columns (named fields, like
<code>name</code> or <code>price</code>). Almost every application you use
— from banking apps to social media — stores its data this way, which makes
SQL one of the most broadly useful languages a developer can learn.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Universal skill.</strong> Nearly every backend system, no matter
the programming language, eventually talks to a SQL database.</li>
<li><strong>Declarative and readable.</strong> You describe the result you
want ("all users older than 18"), not the step-by-step algorithm to find
it.</li>
<li><strong>Powers analytics and reporting.</strong> Business decisions in
most companies are driven by SQL queries run against operational data.</li>
<li><strong>Frequently tested in interviews</strong>, especially for backend,
data engineering, and analytics roles.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Tables, rows, and columns.</strong> A table represents one type
of entity (like <code>users</code> or <code>orders</code>); each row is one
record; each column is one attribute of that record.</p>
<p><strong>SELECT.</strong> The most common SQL statement, used to retrieve
data: <code>SELECT column1, column2 FROM table_name;</code>.</p>
<p><strong>WHERE.</strong> Filters rows based on a condition:
<code>SELECT * FROM users WHERE age &gt; 18;</code>.</p>
<p><strong>ORDER BY.</strong> Sorts the result set:
<code>ORDER BY age DESC</code> sorts from oldest to youngest.</p>
<p><strong>INSERT, UPDATE, DELETE.</strong> The three statements used to
change data: adding new rows, modifying existing ones, and removing rows,
respectively.</p>
<p><strong>Primary key.</strong> A column (or combination of columns) that
uniquely identifies each row in a table — no two rows can share the same
primary key value.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — Selecting specific columns:</strong></p>
<pre><code>SELECT name, email FROM users;
</code></pre>
<p><strong>Example 2 — Filtering with WHERE:</strong></p>
<pre><code>SELECT * FROM users
WHERE age &gt;= 18 AND country = 'India';
</code></pre>
<p><strong>Example 3 — Sorting and limiting results:</strong></p>
<pre><code>SELECT name, score FROM students
ORDER BY score DESC
LIMIT 5;
</code></pre>
<p><strong>Example 4 — Inserting and updating a row:</strong></p>
<pre><code>INSERT INTO users (name, email, age)
VALUES ('Asha', 'asha@example.com', 24);

UPDATE users
SET age = 25
WHERE name = 'Asha';
</code></pre>
""",
        "important_notes": """
<ul>
<li>SQL keywords (<code>SELECT</code>, <code>WHERE</code>, etc.) are
conventionally written in uppercase, but SQL itself is not case-sensitive
for keywords.</li>
<li>Every SQL statement typically ends with a semicolon
(<code>;</code>).</li>
<li><code>UPDATE</code> and <code>DELETE</code> without a
<code>WHERE</code> clause affect <strong>every row</strong> in the table —
always double-check the filter before running these in production.</li>
<li>String values are wrapped in single quotes (<code>'like this'</code>),
while numbers are not.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Forgetting the WHERE clause</strong> on an UPDATE or DELETE
statement, accidentally modifying every row in the table.</li>
<li><strong>Confusing <code>=</code> and <code>==</code></strong> — SQL
uses a single equals sign for equality comparisons.</li>
<li><strong>Mismatched quotes</strong> around string values, causing syntax
errors.</li>
<li><strong>Assuming column order</strong> in <code>INSERT</code> statements
matches table definition order without explicitly listing column names,
which can silently insert data into the wrong columns.</li>
</ul>
""",
        "summary": """
<p>SQL lets you describe what data you want from a relational database using
statements like <code>SELECT</code>, <code>WHERE</code>, <code>ORDER BY</code>,
<code>INSERT</code>, <code>UPDATE</code>, and <code>DELETE</code>. Tables
organize data into rows and columns, with a primary key uniquely identifying
each row. These fundamentals are the entry point into everything else in
relational databases — joins, indexing, and query optimization all build on
top of this basic vocabulary.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Aggregate functions.</strong> Functions like <code>COUNT()</code>,
<code>SUM()</code>, <code>AVG()</code>, <code>MIN()</code>, and
<code>MAX()</code> summarize data across many rows into a single value.</p>
<p><strong>GROUP BY and HAVING.</strong> <code>GROUP BY</code> groups rows
sharing a common value (e.g. all orders from the same customer) so
aggregate functions can be applied per group; <code>HAVING</code> filters
those grouped results, the way <code>WHERE</code> filters individual rows.</p>
<p><strong>Subqueries.</strong> A query nested inside another query, used to
compute an intermediate result — for example, finding all employees earning
more than their department's average salary.</p>
<p><strong>Transactions.</strong> A sequence of statements executed as a
single all-or-nothing unit, guaranteeing that either every change is applied
or none are, even in the face of failures.</p>
<p><strong>Normalization.</strong> The process of structuring tables to
reduce data duplication and inconsistency, typically described through
"normal forms" (1NF, 2NF, 3NF), trading some query simplicity for data
integrity.</p>
""",
        "time_complexity": """
<p>SQL query "complexity" is usually discussed in terms of how the database
engine executes it rather than classic Big-O notation, but the same
intuition applies:</p>
<ul>
<li><strong>Full table scan:</strong> O(n) — the database checks every row
because no index can help.</li>
<li><strong>Indexed lookup:</strong> O(log n) using a typical B-tree index,
or close to O(1) for an exact-match hash index.</li>
<li><strong>Aggregations (GROUP BY, COUNT, SUM):</strong> O(n) at minimum,
since every relevant row must be read at least once.</li>
<li><strong>Joins without proper indexing:</strong> can degrade to O(n·m) for
tables of size n and m, since every row in one table may need to be compared
against every row in the other.</li>
</ul>
""",
        "space_complexity": """
<p>SQL query "space" usually refers to the temporary memory or disk space
the database engine needs while executing a query, separate from the
permanent storage used by the tables themselves:</p>
<ul>
<li><code>ORDER BY</code> and <code>GROUP BY</code> on large result sets may
require temporary sort buffers, which can spill to disk if they exceed
available memory.</li>
<li>Subqueries and joins can materialize intermediate result sets, using
space proportional to their size before the final result is produced.</li>
<li>Indexes themselves consume additional disk space beyond the table
data — a trade-off you accept in exchange for faster reads.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>Write a query to find the second-highest salary in an employees
table.</li>
<li>Explain the difference between <code>WHERE</code> and
<code>HAVING</code>.</li>
<li>Write a query using <code>GROUP BY</code> to count orders per customer.</li>
<li>What is a transaction, and what do the ACID properties (Atomicity,
Consistency, Isolation, Durability) mean?</li>
<li>What is database normalization, and why might you deliberately
denormalize a table?</li>
<li>Write a query to find duplicate rows in a table.</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>E-commerce platforms</strong> use SQL to track inventory, orders,
and customer data with strong consistency guarantees.</li>
<li><strong>Banking systems</strong> rely on transactions to ensure money
transfers either complete fully or not at all, never partially.</li>
<li><strong>Analytics dashboards</strong> use aggregate queries
(<code>GROUP BY</code>, <code>SUM</code>, <code>AVG</code>) to power charts
and business reports.</li>
<li><strong>Content management systems</strong> use SQL to store and query
articles, users, comments, and permissions.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Practice writing queries against a small sample database (many free
ones are available online) rather than only reading about syntax.</li>
<li>Get comfortable reading a query's execution plan
(<code>EXPLAIN</code>) — this is where you actually see whether an index is
being used.</li>
<li>Practice translating plain-English questions ("which customers spent
more than ₹10,000 last month?") directly into SQL — this translation skill
matters more in interviews than memorizing syntax.</li>
<li>Work through GROUP BY + HAVING problems specifically, since they trip
up beginners more than any other clause.</li>
</ul>
""",
    },
}

# ============================================================================
# DATABASE — Joins & Queries
# ============================================================================
TOPIC_CONTENT["joins-queries"] = {
    "basic": {
        "introduction": """
<p>Real-world data is rarely stored in a single table. Customer information
lives in one table, their orders in another, and order items in a third.
<strong>Joins</strong> let you combine rows from two or more tables based on
a related column — usually a foreign key pointing back to another table's
primary key — so you can ask questions that span multiple tables at once.</p>
<p>Beyond basic joins, "queries" in this context refers to the broader set
of tools SQL gives you to shape, filter, and combine data: multi-table joins,
subqueries, and set operations that go beyond a single-table
<code>SELECT</code>.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Relational data needs joining.</strong> Almost no real
application question can be answered from a single table alone.</li>
<li><strong>Avoids data duplication.</strong> Splitting data across related
tables (rather than repeating it everywhere) keeps databases smaller and
more consistent — joins are how you reassemble that data when you need it.</li>
<li><strong>Central to interviews.</strong> Join-based SQL questions are
among the most frequently asked database questions in technical
interviews.</li>
<li><strong>Powers real reporting.</strong> "Show me all orders with
customer names and product details" is a joins problem in virtually every
business application.</li>
</ul>
""",
        "core_concepts": """
<p><strong>INNER JOIN.</strong> Returns only the rows that have matching
values in both tables — if a customer has no orders, they simply won't
appear in the result.</p>
<p><strong>LEFT JOIN (LEFT OUTER JOIN).</strong> Returns every row from the
left table, along with matching rows from the right table — if there's no
match, the right table's columns show as <code>NULL</code>.</p>
<p><strong>RIGHT JOIN.</strong> The mirror image of a left join — every row
from the right table is kept, with unmatched left-table columns showing as
<code>NULL</code>.</p>
<p><strong>FULL OUTER JOIN.</strong> Returns all rows from both tables,
matching where possible and filling in <code>NULL</code> where there's no
match on either side.</p>
<p><strong>Foreign keys.</strong> A column in one table that references the
primary key of another table, forming the "join key" that connects related
rows.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — INNER JOIN customers with their orders:</strong></p>
<pre><code>SELECT customers.name, orders.order_id
FROM customers
INNER JOIN orders ON customers.id = orders.customer_id;
</code></pre>
<p><strong>Example 2 — LEFT JOIN to include customers with no orders:</strong></p>
<pre><code>SELECT customers.name, orders.order_id
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id;
-- Customers with zero orders still appear, with order_id = NULL
</code></pre>
<p><strong>Example 3 — Joining three tables:</strong></p>
<pre><code>SELECT customers.name, orders.order_id, products.name AS product
FROM customers
JOIN orders ON customers.id = orders.customer_id
JOIN order_items ON orders.order_id = order_items.order_id
JOIN products ON order_items.product_id = products.id;
</code></pre>
<p><strong>Example 4 — A subquery inside a WHERE clause:</strong></p>
<pre><code>SELECT name FROM customers
WHERE id IN (
    SELECT customer_id FROM orders WHERE total &gt; 5000
);
</code></pre>
""",
        "important_notes": """
<ul>
<li>Always join on columns that are logically related (typically a foreign
key to a primary key) — joining on the wrong column silently produces
meaningless results rather than an error.</li>
<li>An <code>INNER JOIN</code> can unexpectedly "hide" rows that have no
match — use <code>LEFT JOIN</code> when you need to keep every row from one
side regardless of matches.</li>
<li>Joining tables without a proper condition (a "cross join") produces
every possible combination of rows, which can explode into an enormous
result set.</li>
<li>Column names that exist in more than one joined table must be qualified
with the table name (e.g. <code>orders.id</code> vs.
<code>customers.id</code>) to avoid ambiguity.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Forgetting the ON condition</strong>, accidentally creating a
cross join that multiplies every row in one table by every row in the
other.</li>
<li><strong>Using INNER JOIN when LEFT JOIN was needed</strong>, silently
dropping rows that don't have a match (e.g. customers with no orders
disappearing from a report).</li>
<li><strong>Ambiguous column references</strong> when two joined tables
share a column name, causing errors or unexpected results.</li>
<li><strong>Overusing subqueries</strong> where a straightforward join would
be clearer and often faster.</li>
</ul>
""",
        "summary": """
<p>Joins combine related data spread across multiple tables by matching
foreign keys to primary keys. <code>INNER JOIN</code> keeps only matching
rows, while <code>LEFT</code>/<code>RIGHT</code>/<code>FULL OUTER JOIN</code>
preserve unmatched rows from one or both sides. Subqueries let you nest one
query inside another to compute intermediate results. Together, these tools
let you answer real business questions that span more than one table — which
is the normal case in any relational database.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Self joins.</strong> A table joined to itself, useful for
hierarchical data like an <code>employees</code> table where each row has a
<code>manager_id</code> pointing to another row in the same table.</p>
<p><strong>Correlated subqueries.</strong> A subquery that references a
column from the outer query, re-evaluated once per outer row — powerful, but
can be slow if not written carefully compared to an equivalent join.</p>
<p><strong>Common Table Expressions (CTEs).</strong> The <code>WITH</code>
clause lets you name a subquery and reuse it, making multi-step queries much
more readable than deeply nested subqueries.</p>
<p><strong>Window functions.</strong> Functions like <code>ROW_NUMBER()</code>,
<code>RANK()</code>, and running totals that compute a value across a set of
rows related to the current row, without collapsing them into a single
group the way <code>GROUP BY</code> does.</p>
<p><strong>Set operations.</strong> <code>UNION</code>, <code>INTERSECT</code>,
and <code>EXCEPT</code>/<code>MINUS</code> combine the results of two queries
based on set logic rather than row-by-row matching.</p>
""",
        "time_complexity": """
<ul>
<li><strong>Nested loop join (naive):</strong> O(n·m) — every row of one
table compared against every row of the other.</li>
<li><strong>Hash join:</strong> O(n + m) — builds a hash table from the
smaller table, then scans the larger table once.</li>
<li><strong>Merge join (on sorted/indexed columns):</strong> O(n log n + m
log m) for the sort, or O(n + m) if both inputs are already sorted.</li>
<li><strong>Correlated subqueries</strong> can effectively run once per outer
row, turning what looks like an O(n) query into O(n·m) if not optimized by
the database engine.</li>
</ul>
""",
        "space_complexity": """
<p>Joins can require significant temporary space depending on the strategy
the database chooses:</p>
<ul>
<li>A hash join needs O(min(n, m)) space to build a hash table from the
smaller of the two joined tables.</li>
<li>A merge join needs O(n + m) space if the inputs must first be sorted
and don't already have a usable index.</li>
<li>Multi-table joins can materialize large intermediate result sets before
final filtering, which is why join order and filtering early both matter for
memory usage, not just speed.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>Explain the difference between INNER JOIN, LEFT JOIN, and FULL OUTER
JOIN with an example.</li>
<li>Write a query to find employees who earn more than their manager,
using a self join.</li>
<li>What's the difference between a correlated and a non-correlated
subquery?</li>
<li>Write a query using a window function to rank employees by salary
within each department.</li>
<li>When would you use a CTE instead of a subquery?</li>
<li>Write a query to find customers who placed orders in one month but not
the next, using set operations or a LEFT JOIN.</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>Order management systems</strong> join customers, orders, and
products to generate invoices and shipping details.</li>
<li><strong>HR systems</strong> use self joins to model organizational
hierarchies (employee-to-manager relationships).</li>
<li><strong>Analytics platforms</strong> use window functions to compute
running totals, rankings, and period-over-period comparisons directly in
SQL.</li>
<li><strong>Recommendation engines</strong> often join user activity tables
with product catalogs to compute relevance scores.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>For every join you write, ask "do I want to keep unmatched rows?" —
that single question determines whether you need INNER or an OUTER join.</li>
<li>Practice rewriting correlated subqueries as joins (and vice versa) to
build intuition for when each is clearer or faster.</li>
<li>Learn CTEs early — they make multi-step queries dramatically easier to
read, write, and debug than nested subqueries.</li>
<li>When a query returns unexpectedly few or many rows, check the join
type and join condition first — that's the source of the vast majority of
join bugs.</li>
</ul>
""",
    },
}

# ============================================================================
# DATABASE — Indexing
# ============================================================================
TOPIC_CONTENT["indexing"] = {
    "basic": {
        "introduction": """
<p>An <strong>index</strong> is a separate data structure a database
maintains alongside a table to make lookups on specific columns much faster
— conceptually similar to the index at the back of a textbook, which lets
you find a topic by page number instead of reading every page from the
start.</p>
<p>Without an index, finding a row that matches a condition requires
scanning every row in the table (a "full table scan"). With the right
index, the database can jump almost directly to the matching rows,
dramatically cutting down how much data it needs to examine.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Massive speed difference.</strong> A well-chosen index can turn
a query that scans millions of rows into one that touches only a handful.</li>
<li><strong>Scales with data growth.</strong> As tables grow from thousands
to millions of rows, the gap between an indexed and unindexed query widens
enormously.</li>
<li><strong>Directly affects user experience.</strong> Slow queries caused
by missing indexes are one of the most common real-world performance
problems in production applications.</li>
<li><strong>A favorite interview topic</strong> for backend and database
roles, since it tests both conceptual understanding and practical
judgment.</li>
</ul>
""",
        "core_concepts": """
<p><strong>B-tree index.</strong> The most common type of index, structured
as a balanced tree that keeps values sorted, allowing range queries
(<code>WHERE age &gt; 18</code>) and exact-match lookups in logarithmic
time.</p>
<p><strong>Primary key index.</strong> Most databases automatically create
an index on the primary key, since it's the most common column used to
locate a specific row.</p>
<p><strong>Unique index.</strong> Enforces that no two rows share the same
value in the indexed column(s), in addition to speeding up lookups.</p>
<p><strong>Composite index.</strong> An index built across multiple columns
together (e.g. <code>last_name, first_name</code>), useful when queries
frequently filter or sort by that same combination of columns.</p>
<p><strong>Trade-off: reads vs. writes.</strong> Indexes speed up reads
(<code>SELECT</code>) but slow down writes (<code>INSERT</code>,
<code>UPDATE</code>, <code>DELETE</code>), since the index itself must be
updated every time the underlying data changes.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — Creating a basic index:</strong></p>
<pre><code>CREATE INDEX idx_users_email ON users(email);
</code></pre>
<p><strong>Example 2 — A query that benefits from that index:</strong></p>
<pre><code>SELECT * FROM users WHERE email = 'asha@example.com';
-- Without an index: scans every row
-- With an index on email: jumps almost directly to the match
</code></pre>
<p><strong>Example 3 — Creating a composite index:</strong></p>
<pre><code>CREATE INDEX idx_users_name ON users(last_name, first_name);
</code></pre>
<p><strong>Example 4 — Creating a unique index:</strong></p>
<pre><code>CREATE UNIQUE INDEX idx_users_username ON users(username);
-- Now inserting a duplicate username will fail
</code></pre>
""",
        "important_notes": """
<ul>
<li>Indexes take up <strong>extra disk space</strong> and slow down every
write to the indexed table — don't index columns you rarely filter or sort
by.</li>
<li>A composite index on <code>(A, B)</code> generally helps queries
filtering on <code>A</code> alone, or on <code>A</code> and <code>B</code>
together — but usually does <strong>not</strong> help a query that filters
only on <code>B</code>.</li>
<li>Indexes don't guarantee speed automatically — the database's query
planner decides whether to actually use an available index based on the
query and the data.</li>
<li>Too many indexes on a heavily-written table can noticeably slow down
inserts and updates.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Indexing every column "just in case,"</strong> which bloats
storage and slows down writes without meaningfully helping reads.</li>
<li><strong>Assuming an index is being used</strong> without checking the
query's execution plan — sometimes the database chooses a full scan anyway.</li>
<li><strong>Ignoring column order in composite indexes</strong>, creating an
index that doesn't actually match how the application queries the data.</li>
<li><strong>Wrapping an indexed column in a function</strong> in the
<code>WHERE</code> clause (like <code>WHERE LOWER(email) = ...</code>),
which can prevent the database from using a standard index on that column.</li>
</ul>
""",
        "summary": """
<p>Indexes are auxiliary structures that let a database find matching rows
without scanning an entire table, at the cost of extra storage and slower
writes. B-tree indexes are the default choice for most lookups and range
queries, while composite indexes speed up queries filtering on multiple
columns together. Choosing what to index — and what <em>not</em> to index —
is a balancing act between read performance, write performance, and storage
cost that every backend engineer eventually has to reason about.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Covering indexes.</strong> An index that includes every column a
query needs lets the database answer the query directly from the index
without touching the underlying table at all, which can be significantly
faster.</p>
<p><strong>Index selectivity.</strong> A measure of how many distinct values
exist in a column relative to the total number of rows. High-selectivity
columns (like an email address) benefit greatly from indexing; low-
selectivity columns (like a boolean "is_active" flag) often don't.</p>
<p><strong>Hash indexes.</strong> Some databases support hash-based indexes
optimized for exact-match lookups (O(1) average case) but unable to support
range queries, unlike B-tree indexes.</p>
<p><strong>Partial indexes.</strong> An index built over only a subset of
rows matching a condition (e.g. only <code>WHERE status = 'active'</code>),
reducing index size and write overhead when only a fraction of rows are
frequently queried.</p>
<p><strong>Index maintenance.</strong> As data is inserted, updated, and
deleted, indexes can become fragmented over time, and periodic maintenance
(like rebuilding or reorganizing) may be needed to keep performance
consistent.</p>
""",
        "time_complexity": """
<ul>
<li><strong>B-tree index lookup:</strong> O(log n).</li>
<li><strong>B-tree index range query:</strong> O(log n + k), where k is the
number of matching rows returned.</li>
<li><strong>Hash index exact-match lookup:</strong> O(1) average case.</li>
<li><strong>Full table scan (no usable index):</strong> O(n).</li>
<li><strong>Index insertion/update:</strong> O(log n) per index, which is
why tables with many indexes see slower write throughput.</li>
</ul>
""",
        "space_complexity": """
<p>Each index adds its own storage overhead separate from the table's base
data:</p>
<ul>
<li>A single-column B-tree index typically adds O(n) space, proportional to
the number of rows.</li>
<li>A composite index across multiple columns generally uses more space per
entry than a single-column index, since it stores values for every included
column.</li>
<li>Covering indexes trade additional storage for reduced query time, since
they duplicate the queried columns' data inside the index itself.</li>
<li>A table with several indexes can end up using more disk space for its
indexes combined than for the table data itself, which is an important
capacity-planning consideration.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>Explain how a B-tree index makes a query faster than a full table
scan.</li>
<li>What is a composite index, and how does column order affect which
queries it can help?</li>
<li>What's the difference between a clustered and a non-clustered index?</li>
<li>Why might adding an index sometimes make an application slower overall?</li>
<li>What is index selectivity, and why does it matter when deciding what to
index?</li>
<li>How would you diagnose why a query isn't using an index that already
exists?</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>E-commerce search</strong> relies on indexes over product name,
category, and price to keep filtering fast even with large catalogs.</li>
<li><strong>Login systems</strong> index the username or email column so
authentication lookups stay fast regardless of how many users exist.</li>
<li><strong>Analytics dashboards</strong> use composite and covering indexes
to keep frequently-run reports fast without scanning entire fact tables.</li>
<li><strong>Multi-tenant SaaS applications</strong> often index a
<code>tenant_id</code> column first in composite indexes, since almost
every query filters by tenant.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Practice reading query execution plans (<code>EXPLAIN</code> /
<code>EXPLAIN ANALYZE</code>) to see, concretely, whether an index is being
used and how many rows are actually scanned.</li>
<li>For any table you design, list the queries you expect to run against it
first, then decide on indexes based on those access patterns — not the
other way around.</li>
<li>Experiment with composite index column order on a sample dataset and
observe how it changes which queries can use the index.</li>
<li>Practice explaining the read/write trade-off of indexing out loud —
interviewers often probe for this reasoning, not just the mechanics.</li>
</ul>
""",
    },
}

# ============================================================================
# DATABASE — Query Optimization
# ============================================================================
TOPIC_CONTENT["query-optimization"] = {
    "basic": {
        "introduction": """
<p><strong>Query optimization</strong> is the practice of writing and
tuning SQL so that the database can return correct results as efficiently as
possible — using less time, less memory, and less disk activity. The same
question can often be answered by many different queries that all produce
identical results but perform very differently, and optimization is about
consistently choosing (or rewriting toward) the efficient ones.</p>
<p>Most database engines include a <strong>query optimizer</strong>, a
component that automatically chooses an execution strategy for a given
query — but the optimizer can only work with what you give it. Poorly
structured queries, missing indexes, or unnecessary complexity can prevent
even a smart optimizer from doing its job well.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Directly impacts application speed.</strong> Slow queries are
one of the most common root causes of a sluggish application.</li>
<li><strong>Scales your infrastructure further.</strong> Efficient queries
mean a single database server can handle far more users before you need to
scale hardware.</li>
<li><strong>Reduces cost.</strong> In cloud environments, inefficient
queries directly translate into higher compute and I/O costs.</li>
<li><strong>A key differentiator in interviews</strong> and on the job —
writing a query that "works" is easy; writing one that performs well at
scale is the skill that's actually valued.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Query execution plan.</strong> The step-by-step strategy the
database chooses to execute a query — which indexes to use, which join
algorithm to apply, and in what order to process tables. Most databases let
you inspect this with an <code>EXPLAIN</code> statement.</p>
<p><strong>Selectivity and filtering early.</strong> Applying the most
restrictive filter as early as possible reduces the amount of data later
steps (like joins) need to process.</p>
<p><strong>Avoiding SELECT *.</strong> Requesting only the columns you
actually need reduces the amount of data transferred and can allow the
database to use a covering index instead of touching the full table.</p>
<p><strong>Indexes as an optimization tool.</strong> Well-chosen indexes are
often the single biggest lever for query performance — see the Indexing
topic for details on how they work.</p>
<p><strong>Avoiding functions on indexed columns.</strong> Wrapping a column
in a function inside a <code>WHERE</code> clause (like
<code>WHERE YEAR(created_at) = 2024</code>) can prevent the database from
using an index on that column efficiently.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — Avoid SELECT * when you only need specific
columns:</strong></p>
<pre><code>-- Less efficient: fetches every column, even unused ones
SELECT * FROM orders WHERE customer_id = 42;

-- More efficient: fetches only what's needed
SELECT order_id, total FROM orders WHERE customer_id = 42;
</code></pre>
<p><strong>Example 2 — Filter before joining where possible:</strong></p>
<pre><code>SELECT o.order_id, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'completed';
-- The database can filter orders down first, then join only what's left
</code></pre>
<p><strong>Example 3 — Avoid wrapping indexed columns in functions:</strong></p>
<pre><code>-- Can prevent index usage
SELECT * FROM orders WHERE YEAR(created_at) = 2024;

-- Index-friendly alternative
SELECT * FROM orders
WHERE created_at &gt;= '2024-01-01' AND created_at &lt; '2025-01-01';
</code></pre>
<p><strong>Example 4 — Checking a query's execution plan:</strong></p>
<pre><code>EXPLAIN SELECT * FROM orders WHERE customer_id = 42;
</code></pre>
""",
        "important_notes": """
<ul>
<li>Optimization should be guided by <strong>measurement</strong>
(execution plans, timing) rather than guesswork — what's slow in theory
isn't always slow in practice, and vice versa.</li>
<li><code>SELECT *</code> is convenient during development but frequently
worth avoiding in production code once a query's actual needs are known.</li>
<li>The same logical query can often be written in several different ways;
they are not guaranteed to perform identically even if they return the same
results.</li>
<li>Adding an index is not always the answer — sometimes the query itself,
or the surrounding application logic, is the real bottleneck.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Optimizing without measuring first</strong> — changing a query
based on intuition rather than checking its actual execution plan or
timing.</li>
<li><strong>Over-relying on SELECT *</strong> even in performance-sensitive
code paths, fetching far more data than necessary.</li>
<li><strong>Wrapping filtered columns in functions</strong>, unintentionally
disabling index usage.</li>
<li><strong>Solving every performance problem by adding more indexes</strong>,
without considering the added write overhead and diminishing returns.</li>
</ul>
""",
        "summary": """
<p>Query optimization is about writing SQL that the database can execute
efficiently, guided by real measurement rather than guesswork. Filtering
early, selecting only needed columns, keeping indexed columns free of
wrapping functions, and reading execution plans are all foundational habits.
As data grows, the gap between a "working" query and a genuinely
well-optimized one becomes the difference between an application that feels
instant and one that feels sluggish.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Reading execution plans in depth.</strong> Beyond simply checking
whether an index is used, experienced engineers examine estimated vs.
actual row counts, join algorithms chosen (nested loop, hash, or merge
join), and where the majority of time or I/O is being spent within the
plan.</p>
<p><strong>Query rewriting.</strong> Semantically equivalent queries can
have very different performance profiles — for example, rewriting a
correlated subquery as a join, or replacing <code>NOT IN</code> with
<code>NOT EXISTS</code> to avoid subtle performance and correctness pitfalls
around <code>NULL</code> values.</p>
<p><strong>Caching layers.</strong> Beyond the query itself, application-
level or database-level caching (materialized views, query result caches)
can eliminate repeated work for frequently-run, rarely-changing queries.</p>
<p><strong>Statistics and the query planner.</strong> Databases maintain
internal statistics about data distribution to decide on execution
strategies; stale statistics after large data changes can cause the planner
to make poor choices even with good indexes in place.</p>
<p><strong>Partitioning.</strong> Splitting a very large table into smaller
physical segments (by date range or another key) so queries that only need
recent data can skip scanning older partitions entirely.</p>
""",
        "time_complexity": """
<ul>
<li><strong>Well-optimized indexed query:</strong> O(log n + k), where k is
the number of matching rows.</li>
<li><strong>Poorly optimized query on the same data (full scan):</strong>
O(n), regardless of how few rows actually match.</li>
<li><strong>Query with an unnecessary nested loop join:</strong> can degrade
to O(n·m) where a hash or merge join would have achieved O(n + m).</li>
<li><strong>Repeated execution of an expensive but static query:</strong>
effectively O(1) per call if cached, versus paying the full query cost every
single time without caching.</li>
</ul>
""",
        "space_complexity": """
<p>Optimization often involves trading space for time, or vice versa:</p>
<ul>
<li>Adding indexes trades extra disk space (O(n) per index) for faster
reads.</li>
<li>Materialized views and caches use additional storage to avoid
recomputing expensive query results repeatedly.</li>
<li>Poorly optimized joins can consume large amounts of temporary memory or
disk space for intermediate result sets — one of the reasons filtering early
matters for space, not just speed.</li>
<li>Partitioning doesn't change the total data stored, but changes how much
of it any single query needs to touch, indirectly reducing the working set
size for a given query.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>How would you diagnose a slow-running query in a production database?</li>
<li>What's the difference between <code>NOT IN</code> and
<code>NOT EXISTS</code>, and why might one perform better than the other?</li>
<li>Explain the difference between a nested loop join, a hash join, and a
merge join, and when each is typically chosen.</li>
<li>What is a materialized view, and when would you use one?</li>
<li>How does table partitioning improve query performance for large
tables?</li>
<li>Walk through how you'd optimize a query that joins five tables and
currently takes several seconds to run.</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>High-traffic web applications</strong> depend on optimized
queries to keep page load times low even under heavy concurrent usage.</li>
<li><strong>Data warehouses</strong> use partitioning and materialized views
to keep complex analytical queries fast over very large historical
datasets.</li>
<li><strong>Financial systems</strong> optimize transactional queries
carefully to maintain both speed and strict correctness guarantees under
load.</li>
<li><strong>Search and filtering features</strong> in consumer apps rely on
optimized, well-indexed queries to return results within milliseconds.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Practice reading <code>EXPLAIN ANALYZE</code> output on real queries —
look specifically for full table scans and large differences between
estimated and actual row counts.</li>
<li>Take a slow query you've written before, identify one specific
bottleneck, and rewrite the query to address that bottleneck — repeat this
practice regularly.</li>
<li>Build a habit of asking "what index would help this query?" before
writing a query against a large table, not after it turns out to be slow.</li>
<li>Study a few real query rewriting patterns (subquery-to-join,
NOT IN-to-NOT EXISTS) deeply enough to explain not just what changes, but
why it's faster.</li>
</ul>
""",
    },
}

# ============================================================================
# SYSTEM DESIGN — Scalability
# ============================================================================
TOPIC_CONTENT["scalability"] = {
    "basic": {
        "introduction": """
<p><strong>Scalability</strong> is a system's ability to handle growth —
more users, more data, more requests — without a proportional collapse in
performance. A system that works beautifully for 100 users but grinds to a
halt at 100,000 hasn't failed at its original job; it has failed to
scale.</p>
<p>Designing for scalability means anticipating growth and structuring a
system so that adding more capacity (more servers, more storage, more
bandwidth) actually solves the problem, rather than running into some
architectural wall that no amount of extra hardware can fix.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Growth is the default expectation</strong> for any successful
product — user counts, data volume, and traffic all tend to increase over
time.</li>
<li><strong>Poor scalability directly costs money and users.</strong> Slow
or unreliable systems under load drive users away and increase
infrastructure spend inefficiently.</li>
<li><strong>Central to system design interviews.</strong> Nearly every
system design question ultimately asks "how would this scale?"</li>
<li><strong>Shapes every other decision</strong> — database choice, caching
strategy, and architecture all flow from how much scale a system needs to
support.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Vertical scaling (scaling up).</strong> Adding more resources
(CPU, RAM, disk) to a single existing machine. Simple to reason about, but
eventually hits a hard ceiling — there's a limit to how powerful one machine
can get, and it doesn't protect against that machine failing.</p>
<p><strong>Horizontal scaling (scaling out).</strong> Adding more machines
that share the workload, rather than making one machine bigger. This scales
much further and adds redundancy, but requires the system to be designed to
work across multiple machines.</p>
<p><strong>Stateless vs. stateful services.</strong> A stateless service
doesn't store session-specific data between requests, making it trivial to
run many identical copies behind a load balancer. Stateful services (like
databases) require more careful design to scale horizontally.</p>
<p><strong>Bottlenecks.</strong> The single slowest or most resource-
constrained part of a system, which limits overall throughput no matter how
much you scale everything else.</p>
<p><strong>Throughput and latency.</strong> Throughput measures how many
requests a system handles per unit time; latency measures how long a single
request takes. Scalability efforts often aim to keep both healthy as load
increases.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — Vertical scaling:</strong></p>
<pre><code># Before: 1 server, 4 CPU cores, 8 GB RAM
# After:  1 server, 16 CPU cores, 64 GB RAM
# Same single machine, just bigger
</code></pre>
<p><strong>Example 2 — Horizontal scaling:</strong></p>
<pre><code># Before: 1 web server handling all traffic
# After:  5 identical web servers behind a load balancer,
#         each handling roughly 1/5th of the traffic
</code></pre>
<p><strong>Example 3 — A stateless web request handler:</strong></p>
<pre><code>def handle_request(request):
    user = authenticate(request.token)   # looked up fresh each time
    data = fetch_from_database(user.id)  # no data stored on this server
    return build_response(data)
# Any server instance can handle any request — easy to scale horizontally
</code></pre>
<p><strong>Example 4 — Identifying a bottleneck:</strong></p>
<pre><code># 10 web servers, but only 1 database
# Adding more web servers won't help once the database itself
# becomes the limiting factor
</code></pre>
""",
        "important_notes": """
<ul>
<li>Vertical scaling is simpler but has a <strong>hard physical
ceiling</strong> and a single point of failure — the one machine.</li>
<li>Horizontal scaling requires your application to be designed for it,
typically by keeping servers <strong>stateless</strong> so any request can
go to any server.</li>
<li>Scaling the wrong part of a system doesn't help — always identify the
actual bottleneck before adding capacity.</li>
<li>Scalability isn't only about handling more traffic — it also concerns
data growth (does the database still perform well with 100x more rows?).</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Assuming vertical scaling alone will solve long-term
growth</strong>, without a plan for what happens when a single machine's
limits are reached.</li>
<li><strong>Designing stateful services by default</strong>, making later
horizontal scaling much harder to retrofit.</li>
<li><strong>Adding more servers without identifying the real
bottleneck</strong> (often the database), which doesn't meaningfully improve
performance.</li>
<li><strong>Ignoring data growth</strong> and only thinking about traffic
growth, when both need architectural attention.</li>
</ul>
""",
        "summary": """
<p>Scalability is about designing systems that keep performing well as
usage grows, using vertical scaling (bigger machines) and horizontal scaling
(more machines) as complementary tools. Stateless design is what makes
horizontal scaling practical, and identifying the true bottleneck is
essential before adding capacity anywhere. These fundamentals set up
everything else in system design — load balancing, caching, and
microservices are all, in different ways, tools for achieving scalability.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Database scaling strategies.</strong> <em>Replication</em> copies
data across multiple database servers to spread read load and add
redundancy. <em>Sharding</em> splits data across multiple databases by some
key (like user ID), allowing writes to scale horizontally as well, at the
cost of added complexity for cross-shard queries.</p>
<p><strong>CAP theorem.</strong> In a distributed system, you can only fully
guarantee two of three properties at once during a network partition:
Consistency (every read sees the latest write), Availability (every request
gets a response), and Partition tolerance (the system keeps working despite
network failures). Real systems make deliberate trade-offs here.</p>
<p><strong>Asynchronous processing.</strong> Offloading slow or non-urgent
work (sending emails, generating reports) to background queues/workers
keeps user-facing request paths fast and frees the main system to scale
independently from background workloads.</p>
<p><strong>Auto-scaling.</strong> Automatically adding or removing server
instances based on real-time load metrics, so capacity matches demand
without constant manual intervention.</p>
<p><strong>Read/write splitting.</strong> Directing read queries to
replicas and write queries to a primary database, since most applications
have far more reads than writes and this split lets each scale
independently.</p>
""",
        "time_complexity": """
<p>Scalability is usually reasoned about in terms of throughput and latency
under load rather than classic algorithmic Big-O, but similar thinking
applies:</p>
<ul>
<li><strong>Single-server capacity:</strong> throughput is bounded by that
one machine's CPU, memory, and I/O — a hard ceiling.</li>
<li><strong>Horizontally scaled stateless services:</strong> throughput
scales roughly linearly with the number of servers, up to the point where
some shared resource (like a database) becomes the bottleneck.</li>
<li><strong>Sharded databases:</strong> write throughput scales with the
number of shards, since each shard handles an independent subset of data.</li>
<li><strong>Latency under increasing load</strong> typically stays flat
until a resource saturates, then increases sharply — this "knee" in the
curve is what capacity planning tries to stay ahead of.</li>
</ul>
""",
        "space_complexity": """
<p>"Space" in a scalability context usually refers to storage and memory
footprint across the system as a whole:</p>
<ul>
<li>Replication multiplies storage needs by the number of replicas, trading
storage cost for read capacity and redundancy.</li>
<li>Sharding distributes total storage across multiple machines, so total
space grows with data size but no single machine needs to hold everything.</li>
<li>Caching layers add extra memory usage system-wide in exchange for
reduced load on slower backing stores.</li>
<li>Queues and asynchronous processing pipelines require memory/storage to
hold in-flight messages, which needs capacity planning of its own under
heavy load.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>How would you scale a system from 1,000 to 10 million users?</li>
<li>What's the difference between vertical and horizontal scaling, and when
would you choose one over the other?</li>
<li>Explain the CAP theorem and give an example of a system that prioritizes
availability over consistency.</li>
<li>How would you decide between database replication and sharding for a
growing application?</li>
<li>Design a system that needs to handle a sudden 100x spike in traffic
(e.g. a flash sale).</li>
<li>What are the trade-offs of making a service stateless versus stateful?</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>Streaming platforms</strong> horizontally scale video delivery
across globally distributed servers to handle simultaneous viewers.</li>
<li><strong>E-commerce sites</strong> use auto-scaling and asynchronous
processing to survive massive traffic spikes during sales events.</li>
<li><strong>Social media platforms</strong> shard user data across many
databases to handle billions of posts and interactions.</li>
<li><strong>Ride-sharing apps</strong> scale location and matching services
independently from billing and account services, since their load patterns
differ.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Practice estimating scale before designing: how many users, requests
per second, and data volume are realistic for a given system?</li>
<li>When designing any system, explicitly state where you'd scale
vertically first and where you'd need to scale horizontally from the
start.</li>
<li>Study CAP theorem trade-offs with concrete examples (e.g. a shopping
cart vs. a banking ledger) rather than only the abstract definition.</li>
<li>Practice sketching an architecture diagram and labeling the bottleneck
at each stage of assumed growth (10x, 100x, 1000x users).</li>
</ul>
""",
    },
}

# ============================================================================
# SYSTEM DESIGN — Load Balancing
# ============================================================================
TOPIC_CONTENT["load-balancing"] = {
    "basic": {
        "introduction": """
<p>A <strong>load balancer</strong> sits in front of a group of servers and
distributes incoming requests across them, so no single server gets
overwhelmed while others sit idle. Instead of clients talking directly to
one specific server, they talk to the load balancer, which decides which
backend server should actually handle each request.</p>
<p>This simple idea is what makes horizontal scaling practical — without a
load balancer, adding more servers wouldn't automatically spread traffic
across them; you'd need some mechanism to route requests, and that
mechanism is exactly what a load balancer provides.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Enables horizontal scaling.</strong> Without a load balancer,
running multiple servers doesn't automatically distribute traffic between
them.</li>
<li><strong>Improves reliability.</strong> If one server fails, the load
balancer can detect this and stop routing traffic to it, keeping the
overall system available.</li>
<li><strong>Smooths out uneven load.</strong> Prevents any single server
from becoming a hotspot while others remain underused.</li>
<li><strong>A near-universal component</strong> in system design interview
answers, since almost every scalable architecture includes one.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Load balancing algorithms.</strong> <em>Round robin</em> sends
requests to servers in rotating order; <em>least connections</em> sends
each new request to whichever server currently has the fewest active
connections; <em>IP hash</em> routes a given client consistently to the
same server based on their IP address.</p>
<p><strong>Health checks.</strong> The load balancer periodically checks
whether each backend server is responding correctly, automatically removing
unhealthy servers from rotation until they recover.</p>
<p><strong>Layer 4 vs. Layer 7 load balancing.</strong> Layer 4 (transport
layer) balances based on IP address and port, without looking at the actual
request content. Layer 7 (application layer) can inspect HTTP headers, URLs,
or cookies to make smarter routing decisions.</p>
<p><strong>Sticky sessions.</strong> A technique where a load balancer
routes a specific client's requests to the same server every time, often
used when a service isn't fully stateless.</p>
<p><strong>Single point of failure risk.</strong> The load balancer itself
can become a bottleneck or failure point, which is why production systems
often run multiple load balancers with failover between them.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — Round robin distribution (conceptually):</strong></p>
<pre><code># Requests: R1, R2, R3, R4, R5, R6
# Servers:  A,  B,  C
# R1 -&gt; A, R2 -&gt; B, R3 -&gt; C, R4 -&gt; A, R5 -&gt; B, R6 -&gt; C
</code></pre>
<p><strong>Example 2 — A simple health check:</strong></p>
<pre><code># Every 10 seconds, the load balancer sends:
GET /health HTTP/1.1

# If a server responds 200 OK, keep it in rotation.
# If it fails 3 checks in a row, remove it until it recovers.
</code></pre>
<p><strong>Example 3 — Least connections routing (conceptually):</strong></p>
<pre><code># Server A: 12 active connections
# Server B: 4 active connections
# Server C: 9 active connections
# Next request goes to Server B (fewest active connections)
</code></pre>
<p><strong>Example 4 — Layer 7 routing based on the URL path:</strong></p>
<pre><code># /api/*    -&gt; routed to the API service cluster
# /images/* -&gt; routed to the media service cluster
# /*        -&gt; routed to the main web service cluster
</code></pre>
""",
        "important_notes": """
<ul>
<li>Load balancing only helps if backend servers can genuinely handle
requests <strong>independently</strong> — stateful servers complicate this.</li>
<li><strong>Health checks are essential</strong> — without them, a load
balancer keeps sending traffic to a failed server, making outages worse
rather than better.</li>
<li>Sticky sessions can undermine load balancing's benefits if one server
ends up handling a disproportionate share of "sticky" clients.</li>
<li>A load balancer is itself a piece of infrastructure that can fail —
production systems typically run more than one to avoid a new single point
of failure.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Assuming a load balancer fixes an underlying bottleneck</strong>
elsewhere in the system, like an overloaded shared database.</li>
<li><strong>Forgetting health checks</strong>, allowing traffic to keep
flowing to servers that are already failing.</li>
<li><strong>Overusing sticky sessions</strong> for convenience, which
reduces the effectiveness of load distribution and complicates scaling.</li>
<li><strong>Treating the load balancer as infallible</strong>, without
planning for its own failure or redundancy.</li>
</ul>
""",
        "summary": """
<p>Load balancers distribute incoming traffic across multiple backend
servers, enabling horizontal scaling and improving reliability through
health checks that route around failed servers. Algorithms like round robin,
least connections, and IP hash offer different trade-offs, and the choice
between Layer 4 and Layer 7 load balancing determines how much routing
intelligence is available. A load balancer is a small idea with an outsized
impact — it's often the very first piece of infrastructure that turns "one
server" into "a scalable system."</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Global vs. local load balancing.</strong> Local load balancing
distributes traffic across servers within a single data center; global
(often DNS-based) load balancing routes users to the nearest or healthiest
data center entirely, adding a geographic dimension to load distribution.</p>
<p><strong>Weighted load balancing.</strong> Assigning different weights to
servers with different capacities, so a more powerful server receives
proportionally more traffic than a smaller one.</p>
<p><strong>Consistent hashing.</strong> A technique that minimizes how much
traffic gets rerouted when servers are added or removed, by mapping both
requests and servers onto a hash ring rather than a simple modulo-based
assignment.</p>
<p><strong>Load balancer high availability.</strong> Running load balancers
in an active-passive or active-active pair, often using a floating/virtual
IP address, so the load balancing layer itself has no single point of
failure.</p>
<p><strong>Rate limiting and circuit breaking.</strong> Increasingly, load
balancers and API gateways also protect backend services from being
overwhelmed by capping request rates or temporarily "opening the circuit" to
a failing downstream service.</p>
""",
        "time_complexity": """
<ul>
<li><strong>Round robin selection:</strong> O(1) per request.</li>
<li><strong>Least connections selection (naive):</strong> O(n) to scan all
servers for the minimum, or O(log n) with a suitable priority-queue-like
structure.</li>
<li><strong>Consistent hashing lookup:</strong> O(log n) using a sorted
structure of hash ring positions.</li>
<li><strong>Health check overhead:</strong> effectively O(1) per server per
interval, but scales with the total number of backend servers being
monitored.</li>
</ul>
""",
        "space_complexity": """
<p>A load balancer's own memory footprint is typically small relative to
the systems it manages, but a few things scale with cluster size:</p>
<ul>
<li>Tracking active connections per server for "least connections" routing
uses O(n) space, proportional to the number of backend servers.</li>
<li>Consistent hashing rings use additional space for virtual nodes (often
several per physical server) to improve distribution evenness.</li>
<li>Sticky session tracking requires storing a mapping from client to
server, using space proportional to the number of active clients — this
can become significant at very large scale.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>What load balancing algorithms do you know, and when would you choose
each one?</li>
<li>How does a load balancer detect and handle a failed backend server?</li>
<li>Explain the difference between Layer 4 and Layer 7 load balancing.</li>
<li>How would you avoid the load balancer itself becoming a single point of
failure?</li>
<li>What is consistent hashing, and why is it useful for load balancing
across a changing set of servers?</li>
<li>Design a global load balancing strategy for a service with users
spread across multiple continents.</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>Cloud provider load balancers</strong> (like managed load
balancing services) sit in front of nearly every scalable web application
deployed today.</li>
<li><strong>Content delivery networks (CDNs)</strong> use global load
balancing to route users to the nearest edge server.</li>
<li><strong>API gateways</strong> combine load balancing with rate limiting
and authentication to protect backend microservices.</li>
<li><strong>Distributed caches and databases</strong> use consistent
hashing internally to distribute data (not just requests) evenly across
nodes.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Practice explaining the trade-offs between round robin, least
connections, and IP hash with concrete scenarios where each shines or
struggles.</li>
<li>Work through a consistent hashing example by hand — placing a few nodes
and requests on a ring — until the "minimal rerouting on server changes"
benefit feels concrete rather than abstract.</li>
<li>In system design practice, always ask "what happens if this component
fails?" about the load balancer itself, not just the backend servers.</li>
<li>Practice sketching both Layer 4 and Layer 7 load balancing setups for
the same system and articulating why you'd choose one over the other.</li>
</ul>
""",
    },
}

# ============================================================================
# SYSTEM DESIGN — Caching
# ============================================================================
TOPIC_CONTENT["caching"] = {
    "basic": {
        "introduction": """
<p>A <strong>cache</strong> is a temporary storage layer that keeps a copy
of frequently accessed or expensive-to-compute data close at hand, so future
requests for that same data can be served much faster than recomputing or
re-fetching it from the original source every time.</p>
<p>The core idea is simple: if fetching something is slow but you'll likely
need it again soon, save a copy somewhere fast. The hard part is deciding
<em>what</em> to cache, <em>where</em> to cache it, and <em>when</em> a
cached copy should be thrown away because it's gone stale.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Dramatically reduces latency.</strong> Serving data from memory
is typically orders of magnitude faster than recomputing it or fetching it
from disk or a remote database.</li>
<li><strong>Reduces load on backend systems.</strong> Every request served
from cache is one less request hitting the database or an expensive
computation.</li>
<li><strong>Improves scalability.</strong> Caching lets a system serve far
more traffic without a proportional increase in backend resources.</li>
<li><strong>A near-universal building block</strong> in system design
interviews, appearing in almost every scalable architecture discussion.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Cache hit vs. cache miss.</strong> A <em>hit</em> means the
requested data was found in the cache and returned quickly; a <em>miss</em>
means it wasn't there, so the system must fetch it from the original
source and (usually) store it in the cache for next time.</p>
<p><strong>Where caches live.</strong> <em>Client-side</em> caches (like a
browser cache) store data on the user's device; <em>server-side/in-memory</em>
caches (like Redis or Memcached) sit close to the application; <em>CDN</em>
caches store content geographically close to users.</p>
<p><strong>Time-to-live (TTL).</strong> A duration after which a cached
entry is considered stale and should be refreshed or discarded, balancing
freshness against cache effectiveness.</p>
<p><strong>Cache invalidation.</strong> The process of removing or updating
cached data when the underlying source data changes, so users don't see
outdated information indefinitely.</p>
<p><strong>Eviction policies.</strong> Since cache storage is limited,
policies like <em>Least Recently Used (LRU)</em> decide which entries to
remove first when the cache is full.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — A simple in-memory cache in Python:</strong></p>
<pre><code>cache = {}

def get_user(user_id):
    if user_id in cache:
        return cache[user_id]          # cache hit
    user = fetch_user_from_database(user_id)  # cache miss
    cache[user_id] = user
    return user
</code></pre>
<p><strong>Example 2 — Adding a time-to-live:</strong></p>
<pre><code>import time

cache = {}
TTL_SECONDS = 60

def get_price(product_id):
    entry = cache.get(product_id)
    if entry and time.time() - entry["cached_at"] &lt; TTL_SECONDS:
        return entry["value"]
    price = fetch_price_from_database(product_id)
    cache[product_id] = {"value": price, "cached_at": time.time()}
    return price
</code></pre>
<p><strong>Example 3 — Invalidating a cache entry on update:</strong></p>
<pre><code>def update_user(user_id, new_data):
    save_to_database(user_id, new_data)
    cache.pop(user_id, None)   # remove the now-stale cached copy
</code></pre>
<p><strong>Example 4 — A very small LRU eviction sketch:</strong></p>
<pre><code># Cache capacity: 2
# Access order:   A, B, A, C
# After accessing C, the cache is full (A, B) and must evict
# the Least Recently Used entry -&gt; B is evicted (A was just re-used)
</code></pre>
""",
        "important_notes": """
<ul>
<li>Caching introduces the risk of <strong>stale data</strong> — always
have a clear plan for when and how cached data gets refreshed.</li>
<li>Not everything should be cached — data that changes constantly or is
rarely re-requested may not benefit at all.</li>
<li>A cache with no eviction policy will keep growing until it runs out of
memory — always set a capacity limit and an eviction strategy.</li>
<li>Cache invalidation is famously one of the trickiest problems in
computing — plan for it explicitly rather than as an afterthought.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Caching data without an invalidation plan</strong>, leading to
users seeing stale information indefinitely.</li>
<li><strong>Setting no TTL or eviction policy</strong>, allowing the cache
to grow unbounded and eventually exhaust memory.</li>
<li><strong>Caching highly personalized or rapidly changing data</strong>
that provides little benefit but adds complexity.</li>
<li><strong>Forgetting to handle cache misses gracefully</strong>, causing
errors instead of falling back to the original data source.</li>
</ul>
""",
        "summary": """
<p>Caching stores a copy of frequently needed data somewhere faster to
access, reducing latency and backend load at the cost of managing staleness.
TTLs, invalidation strategies, and eviction policies like LRU are the tools
that keep a cache both effective and correct. Getting caching right is often
one of the highest-leverage performance improvements available in a system —
and one of the trickiest to get exactly right.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Cache-aside (lazy loading).</strong> The application checks the
cache first; on a miss, it loads data from the source, stores it in the
cache, and returns it. Simple and widely used, but the first request after a
miss is always slow.</p>
<p><strong>Write-through cache.</strong> Every write goes to the cache and
the underlying data store simultaneously, keeping them in sync at the cost
of slightly slower writes.</p>
<p><strong>Write-behind (write-back) cache.</strong> Writes go to the cache
immediately and are asynchronously flushed to the backing store later,
improving write latency but risking data loss if the cache fails before
flushing.</p>
<p><strong>Distributed caching.</strong> A cache spread across multiple
nodes (like a Redis cluster), often using consistent hashing to decide which
node owns which keys, allowing the cache itself to scale horizontally.</p>
<p><strong>Cache stampede (thundering herd).</strong> When a popular cache
entry expires, many simultaneous requests can all miss at once and hammer
the backing store; techniques like request locking or staggered expiration
help prevent this.</p>
""",
        "time_complexity": """
<ul>
<li><strong>Cache hit lookup (hash-based cache):</strong> O(1) average
case.</li>
<li><strong>Cache miss (fetch from source):</strong> depends entirely on the
underlying data source — O(log n) for an indexed database lookup, O(n) for
an unindexed one.</li>
<li><strong>LRU eviction with a hash map + doubly linked list:</strong> O(1)
for both reads and updates to recency order.</li>
<li><strong>Distributed cache lookup with consistent hashing:</strong>
O(log n) to determine which node owns a key, plus network round-trip time
to that node.</li>
</ul>
""",
        "space_complexity": """
<p>Caching is fundamentally a space-for-time trade: you spend memory to
save computation or I/O time.</p>
<ul>
<li>An in-memory cache uses O(k) space, where k is the number of entries
currently cached, bounded by the configured capacity.</li>
<li>An LRU cache implementation typically uses an additional O(k) space for
its ordering structure (a doubly linked list alongside the hash map).</li>
<li>Distributed caches multiply memory usage across nodes but allow total
cache capacity to scale well beyond what a single machine could hold.</li>
<li>Write-behind caching adds a temporary in-memory queue of pending writes,
whose size depends on write volume and flush frequency.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>Design an LRU cache with O(1) get and put operations.</li>
<li>What's the difference between cache-aside, write-through, and
write-behind caching strategies?</li>
<li>How would you prevent a cache stampede on a very popular cache key?</li>
<li>How does a distributed cache decide which node stores a given key?</li>
<li>Design a caching layer for a news website's homepage that updates every
few minutes.</li>
<li>What are the risks of caching, and how would you mitigate them in a
system handling sensitive data?</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>Content delivery networks (CDNs)</strong> cache static assets
(images, videos, scripts) close to users around the world.</li>
<li><strong>Web applications</strong> cache database query results in Redis
or Memcached to avoid repeated expensive queries.</li>
<li><strong>Browsers</strong> cache pages, images, and scripts locally so
repeat visits load near-instantly.</li>
<li><strong>API rate-limited services</strong> cache responses from
third-party APIs to avoid exceeding usage limits and reduce cost.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Implement an LRU cache from scratch at least once — it's a common
interview question and builds real intuition for hash map + linked list
combinations.</li>
<li>For every caching design, explicitly state your invalidation strategy —
interviewers frequently probe here since it's the hardest part in
practice.</li>
<li>Practice reasoning about cache hit ratio: what fraction of requests
would realistically be served from cache for a given access pattern?</li>
<li>Study cache stampede prevention techniques (locking, jitter/staggered
TTLs) since they come up in more advanced system design discussions.</li>
</ul>
""",
    },
}

# ============================================================================
# SYSTEM DESIGN — Microservices
# ============================================================================
TOPIC_CONTENT["microservices"] = {
    "basic": {
        "introduction": """
<p>A <strong>microservices</strong> architecture structures an application
as a collection of small, independent services, each responsible for one
specific piece of business functionality — like "user accounts," "payments,"
or "notifications" — communicating with each other over a network. This is
in contrast to a <strong>monolith</strong>, where all functionality lives
together in a single, large application.</p>
<p>Each microservice can be developed, deployed, and scaled independently by
its own team, using whatever technology fits the job best. This
independence is the whole point — and also the source of most of the
architecture's added complexity.</p>
""",
        "why_it_matters": """
<ul>
<li><strong>Independent scaling.</strong> A service under heavy load (like
image processing) can be scaled up without scaling the entire
application.</li>
<li><strong>Independent deployment.</strong> Teams can ship updates to their
own service without coordinating a release of the entire system.</li>
<li><strong>Fault isolation.</strong> A failure in one service doesn't
necessarily bring down the whole application, if designed carefully.</li>
<li><strong>Extremely common in modern system design interviews</strong>,
especially for questions about designing large-scale platforms.</li>
</ul>
""",
        "core_concepts": """
<p><strong>Monolith vs. microservices.</strong> A monolith is a single
deployable unit containing all functionality; microservices split that same
functionality into many independently deployable services.</p>
<p><strong>Service boundaries.</strong> Each microservice should own a
distinct area of business responsibility (often called a "bounded context"),
with its own data, rather than several services sharing one database.</p>
<p><strong>Inter-service communication.</strong> Services typically
communicate via HTTP/REST APIs for direct request-response interactions, or
message queues for asynchronous, decoupled communication.</p>
<p><strong>API gateway.</strong> A single entry point that routes external
requests to the appropriate internal microservice, often also handling
authentication, rate limiting, and logging.</p>
<p><strong>Independent databases.</strong> Each microservice typically
manages its own database, avoiding tight coupling through shared tables
that would undermine independent deployment.</p>
""",
        "simple_examples": """
<p><strong>Example 1 — A monolith's structure (conceptually):</strong></p>
<pre><code># One application, one deployment
app/
  users/
  orders/
  payments/
  notifications/
# All modules share one codebase, one database, one deployment pipeline
</code></pre>
<p><strong>Example 2 — The same functionality as microservices:</strong></p>
<pre><code>user-service/       (own database, own deployment)
order-service/       (own database, own deployment)
payment-service/     (own database, own deployment)
notification-service/(own database, own deployment)
</code></pre>
<p><strong>Example 3 — A service-to-service HTTP call:</strong></p>
<pre><code># order-service needs to verify the user exists
response = http_get("http://user-service/api/users/42")
if response.status == 200:
    proceed_with_order()
</code></pre>
<p><strong>Example 4 — Asynchronous communication via a message queue:</strong></p>
<pre><code># order-service publishes an event; it doesn't wait for a response
publish_event("order_placed", {"order_id": 501, "user_id": 42})

# notification-service listens for this event independently
def on_order_placed(event):
    send_confirmation_email(event["user_id"], event["order_id"])
</code></pre>
""",
        "important_notes": """
<ul>
<li>Microservices add real <strong>operational complexity</strong> —
network calls, service discovery, and distributed debugging all become
harder than in a monolith.</li>
<li>Each service ideally owns its own data — <strong>sharing a database
directly between services</strong> defeats much of the purpose and
reintroduces tight coupling.</li>
<li>Not every application needs microservices — for small teams or early-
stage products, a well-structured monolith is often simpler and faster to
build correctly.</li>
<li>Network calls between services can fail in ways in-process function
calls never do — timeouts, partial failures, and retries all need explicit
handling.</li>
</ul>
""",
        "common_mistakes": """
<ul>
<li><strong>Splitting into microservices prematurely</strong>, before the
team or product is large enough to benefit, adding complexity without
payoff.</li>
<li><strong>Sharing a single database across multiple services</strong>,
which recreates monolith-style coupling while keeping microservice-style
operational overhead.</li>
<li><strong>Ignoring network failure modes</strong>, assuming service calls
will always succeed the way local function calls do.</li>
<li><strong>Drawing service boundaries around technical layers</strong>
(like "database service" or "UI service") instead of business
capabilities, which tends to produce services that must always change
together anyway.</li>
</ul>
""",
        "summary": """
<p>Microservices break an application into small, independently deployable
services, each owning a specific piece of business functionality and often
its own database. This unlocks independent scaling, deployment, and fault
isolation, at the cost of added operational complexity around network
communication, service coordination, and distributed debugging. The
decision to adopt microservices should be driven by real organizational and
scaling needs, not architecture for its own sake.</p>
""",
    },
    "intermediate": {
        "advanced_concepts": """
<p><strong>Service discovery.</strong> As services scale up and down
dynamically, a service discovery mechanism (like a registry) tracks which
instances of a service are currently available, so callers don't need
hardcoded addresses.</p>
<p><strong>Circuit breakers.</strong> A pattern that detects when a
downstream service is failing repeatedly and "opens the circuit," failing
fast instead of piling up requests against a service that's already
struggling — preventing cascading failures across the system.</p>
<p><strong>Saga pattern.</strong> Since a single transaction can no longer
span multiple databases the way it could in a monolith, sagas coordinate a
sequence of local transactions across services, using compensating actions
to undo earlier steps if a later step fails.</p>
<p><strong>Event-driven architecture.</strong> Services communicate by
publishing and subscribing to events on a message bus, decoupling producers
from consumers and enabling services to react to changes without direct,
synchronous calls.</p>
<p><strong>Observability.</strong> Distributed tracing, centralized logging,
and metrics become essential in a microservices architecture, since a
single user request may touch many services and a failure could originate
anywhere along that path.</p>
""",
        "time_complexity": """
<p>Microservices performance is usually discussed in terms of request
latency and system throughput rather than classic algorithmic complexity:</p>
<ul>
<li><strong>A single-service, single-database request:</strong> latency
dominated by that one service's processing and database query time.</li>
<li><strong>A request spanning multiple services (synchronous calls):</strong>
latency accumulates across each network hop, so a chain of 5 services each
taking 20ms can add up to 100ms or more just in inter-service
communication.</li>
<li><strong>Parallel service calls</strong> (calling multiple independent
services concurrently rather than one after another) reduce total latency to
roughly the slowest single call rather than the sum of all calls.</li>
<li><strong>Asynchronous/event-driven flows</strong> decouple the "request
completion" latency from the full end-to-end processing time, since later
steps happen in the background.</li>
</ul>
""",
        "space_complexity": """
<p>"Space" in a microservices context typically refers to infrastructure
footprint rather than an algorithm's memory usage:</p>
<ul>
<li>Each microservice typically runs multiple instances for redundancy,
multiplying the baseline memory/CPU footprint compared to a single
monolith deployment.</li>
<li>Duplicated data across services (each with its own database) trades
additional storage for independence — the same conceptual entity, like a
"user," might be partially represented in several services' databases.</li>
<li>Message queues and event logs used for asynchronous communication
require their own storage capacity, scaling with message volume and
retention settings.</li>
<li>Observability tooling (logs, traces, metrics) adds its own storage
footprint, which tends to grow substantially with the number of services and
requests in the system.</li>
</ul>
""",
        "interview_questions": """
<ul>
<li>What are the trade-offs between a monolithic and a microservices
architecture?</li>
<li>How would you handle a transaction that needs to update data across
multiple microservices?</li>
<li>What is a circuit breaker, and why is it important in a microservices
architecture?</li>
<li>How does service discovery work, and why is it needed in a dynamic,
auto-scaling environment?</li>
<li>Design a microservices architecture for an e-commerce platform,
identifying the main services and how they'd communicate.</li>
<li>How would you debug a slow request that passes through five different
microservices?</li>
</ul>
""",
        "real_world_applications": """
<ul>
<li><strong>Large streaming platforms</strong> split functionality like
user profiles, recommendations, billing, and video encoding into
independent, separately scaled services.</li>
<li><strong>E-commerce platforms</strong> commonly separate inventory,
checkout, payments, and shipping into distinct microservices, each with
their own release cadence.</li>
<li><strong>Ride-sharing platforms</strong> run independent services for
matching, pricing, mapping, and payments, since each has very different
scaling and reliability needs.</li>
<li><strong>Banking and fintech systems</strong> increasingly split legacy
monoliths into microservices to allow safer, incremental modernization
without a full system rewrite.</li>
</ul>
""",
        "practice_tips": """
<ul>
<li>Practice identifying service boundaries around business capabilities
("orders," "payments") rather than technical layers — this is the single
most common design mistake to avoid.</li>
<li>For any microservices design, explicitly walk through what happens when
one service is temporarily unavailable — this reveals whether your design
actually achieves fault isolation.</li>
<li>Study the saga pattern with a concrete example (like an order that needs
payment, inventory, and shipping to all succeed) until the compensating-
action idea feels natural.</li>
<li>When practicing system design interviews, explicitly justify <em>why</em>
microservices are (or aren't) the right choice for the scenario, rather than
defaulting to them automatically.</li>
</ul>
""",
    },
}
