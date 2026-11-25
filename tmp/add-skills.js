(async () => {
  // JD-aligned skills, exact portal wording (already-added ones are skipped automatically)
  const SKILLS = [
    "Data Structures, Algorithms, Object-Oriented Programming (OOP), and Operating Systems.",
    "Programming",
    "PROGRAMMING KNOWLEDGE, BASIC PROGRAMMING FUNDAMENTALS",
    "Basic knowledge of Programming",
    "Knowledge in computer languages C, C++, Dot net, Java, Python",
    "python",
    "C++",
    "Java",
    "Javascript",
    "HTML",
    "CSS",
    "Angular",
    "Web  Programming",
    "web programming",
    "web applications",
    "Web Basics",
    "Java Full  Stack Development",
    "Software development",
    "Knowledge in software development,designing, development, and debugging",
    "Design and Development",
    "SDLC",
    "Software Testing",
    "Testing",
    "Testing & Validation",
    "Software Maintenance",
    "Technical Skills, Analytical Skills, Software Testing, Project Management",
    "Should have basic skill set of AI and how to perform UAT",
    "Artificial Intelligence and Machine Learning",
    "Artificial Intelligence and Mechine Learning",
    "AI/ML",
    "AI and machine learning concepts",
    "AI,",
    "AI solution",
    "Generative AI",
    "large number modules (LLM)",
    "Artificial Intelligence & Data Science",
    "data science",
    "Datascience Analyst",
    "Data Preprocessing",
    "Feature Engineering",
    "Data Analytics",
    "Data Analystics",
    "Data Analytics, Problem Solving",
    "Data Visualisation",
    "Statistics",
    "Knowledge in descriptive statistics",
    "Ability to analyze data and provide meaningful insights",
    "Ability to analyse complex data",
    "SQL",
    "SQL Server",
    "MSSQL",
    "Database",
    "Database Management",
    "Basic knowledge of Databases",
    "Relational/Non Relation Database Knowledge",
    "Analytical Skills",
    "Problem Solving",
    "Problem-Solving",
    "Attention to Detail",
    "Communication Skills",
    "Communication, Problem Solving, Analytical Skills",
    "Technical Proficiency, Analytical Skills, Attention to Detail, Problem-Solving, Communication Skills",
    "COMPUTER SCIENCE/IT, ATTENTION TO DETAIL, ANALYTICAL SKILLS,",
    "Strong analytical and quantitative skills",
    "Problem solving with good technical skills",
    "Critical Thinking, Communication, Adaptability, Attention to detail",
    "Analytical Skills, Communication Skills, Learning Agility",
    "computer science",
    "Computer Science/IT",
    "IT/Computer Science",
    "B.E./BTech (CS/IT)",
    "computer engineering",
    "Btech pursuing",
    "Technical Proficiency",
    "technical learning",
  ];

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const norm = s => s.toLowerCase().replace(/\s+/g, " ").trim();

  const label = [...document.querySelectorAll("label, span, div, p")]
    .find(el => /^my skill/i.test(el.textContent.trim()) && el.textContent.length < 40);
  if (!label) return console.error("❌ 'My Skill(s)' label not found");
  let box = label, input = null;
  for (let i = 0; i < 6 && !input; i++) {
    box = box.parentElement;
    input = box.querySelector("input:not([type=hidden]):not([type=checkbox])");
  }
  if (!input) return console.error("❌ Skills input not found");
  const field = input.closest(".ng-select, [class*='select']") || box;

  const chips = () => [...field.querySelectorAll(".ng-value-label, [class*='multi-value__label'], [class*='chip'], [class*='tag']")]
    .map(c => norm(c.textContent.replace("×", "")));

  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
  const type = v => {
    setter.call(input, v);
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true, key: v.slice(-1) || "a" }));
  };
  const OPTION_SEL = ".ng-option, [role=option], [class*='option']";

  const added = [], skipped = [], already = [];

  for (const skill of SKILLS) {
    if (chips().includes(norm(skill))) { already.push(skill); continue; } // clicking again would REMOVE it

    input.focus(); input.click();
    type(skill);

    let pick = null;
    for (let t = 0; t < 15 && !pick; t++) {
      await sleep(200);
      pick = [...document.querySelectorAll(OPTION_SEL)]
        .find(o => o.offsetParent !== null && norm(o.textContent) === norm(skill)); // exact only
    }

    if (pick) {
      ["mousedown", "mouseup", "click"].forEach(e =>
        pick.dispatchEvent(new MouseEvent(e, { bubbles: true })));
      added.push(skill);
      console.log("➕", skill);
    } else {
      skipped.push(skill);
      console.warn("⏭️ not found:", skill);
    }
    type("");
    await sleep(400);
  }

  console.log(`\n✅ Added ${added.length}`, added);
  console.log(`☑️ Already there ${already.length}`, already);
  console.log(`⏭️ Skipped ${skipped.length}`, skipped);
  console.log("👉 Check the chips, then click Save yourself.");
})();
