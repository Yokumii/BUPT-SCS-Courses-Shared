(() => {
  'use strict';

  const REQUIRED_HEADERS = [
    '课程体系', '课程编号', '课程名称', '完成情况', '课程性质', '课程属性', '学分', '通选课类别',
  ];
  const INNOVATION_REQUIRED_HEADERS = [
    '序号', '学年学期', '级别', '创新学分类别', '项目/课程名称', '学分', '成绩',
  ];

  const COURSES = {
    politicsRequired: {
      '3322100012': '思想道德与法治',
      '3322100060': '中国近现代史纲要',
      '3322100021': '马克思主义基本原理',
      '3322100083': '毛泽东思想和中国特色社会主义理论体系概论',
      '3322100092': '习近平新时代中国特色社会主义思想概论',
      '1052100010': '形势与政策1',
      '1052100020': '形势与政策2',
      '1052100030': '形势与政策3',
      '1052100040': '形势与政策4',
      '1052100050': '形势与政策5',
    },
    history: {
      '3322111010': '中共党史',
      '3322111006': '中华人民共和国史',
      '3322111011': '改革开放史',
      '3322111012': '社会主义发展史',
    },
    generalRequired: {
      '3812150010': '体育基础',
      '2122110002': '军事理论',
      '2122120000': '大学生心理健康',
      '2122100090': '安全教育',
      '3132140020': '工程师职业素养',
      '3132140050': '科技交流能力训练',
    },
    mathRequired: {
      '3412110073': '线性代数',
      '3412120031': '大学物理C',
    },
    discipline: {
      '3132112011': '计算导论与程序设计',
      '3122101024': '电路与电子学基础',
      '3132112020': '离散数学（上）',
      '3132112030': '离散数学（下）',
      '3132113020': '数字逻辑与数字系统',
      '3132112040': '形式语言与自动机',
    },
    professionalFoundation: {
      '3132121320': '数据结构',
      '3132111040': '算法设计与分析',
      '3132113150': '计算机系统基础',
      '3132111010': '操作系统',
      '3132111021': '编译原理与技术',
      '3132113041': '计算机组成原理',
      '3132113060': '计算机系统结构',
      '3132121030': '计算机网络',
      '3132111030': '数据库系统原理',
      '3132112050': '软件工程',
      '3132121040': '现代交换原理',
    },
    practiceRequired: {
      '2122110003': '军训',
      '3322100013': '思想道德与法治（实践环节）',
      '3322100061': '中国近现代史纲要（实践环节）',
      '3322100022': '马克思主义基本原理（实践环节）',
      '3322100084': '毛泽东思想和中国特色社会主义理论体系概论（实践环节）',
      '3412130048': '物理实验A',
      '3132102410': '计算机系统基础实践',
      '3132102002': '毕业设计',
    },
  };

  const CALCULUS_GROUPS = [
    ['3412110012', '3412110021'],
    ['3412110051', '3412110062'],
  ];
  const PROBABILITY = ['3412110092', '3412110102'];
  const MATH_ELECTIVE = ['3412110150', '3412110160', '3412110170', '3412160061'];
  const PROFESSIONAL_MODULES = {
    network: new Set([
      '3132121120', '3132121130', '3132121310', '3132121350', '3132121300', '3132111080', '3132133010',
    ]),
    data: new Set(['3132132120', '3132123090', '3132112100', '3132123080', '3132132020']),
    extension: new Set([
      '3132121290', '3132103030', '3132111060', '3132113110', '3132103020', '3132112080', '3132121080',
      '3132121270', '3132114060', '3132114070', '3132113090', '3132113160', '3132111090', '3132114041',
    ]),
  };
  const ALL_PROFESSIONAL_ELECTIVES = new Set(Object.values(PROFESSIONAL_MODULES).flatMap((set) => [...set]));
  const ALL_FIXED_CODES = new Set(
    Object.values(COURSES).flatMap((courses) => Object.keys(courses)),
  );

  const PRACTICE_GROUPS = [
    { label: '程序设计入门实践（二选一）', count: 1, codes: ['3132102380', '3132102390'] },
    { label: '面向对象程序设计实践（二选一）', count: 1, codes: ['3132102470', '3132102321'] },
    { label: '组成/数字逻辑课程设计（二选一）', count: 1, codes: ['3132102060', '3132102070'] },
    { label: '操作系统/编译课程设计（二选一）', count: 1, codes: ['3132102080', '3132102100'] },
    { label: '数据结构/网络/数据库课程设计（三选二）', count: 2, codes: ['3132102022', '3132102120', '3132102090'] },
  ];
  const COLLEGE_FIXED_PATTERN = /创新创业实践课|现代信息技术创新与实践/;
  const COLLEGE_PRACTICE_PATTERN =
    /大数据技术实践训练|智能车实践训练|智能机器人实践训练|移动应用开发实践训练|机器学习实践训练|科研训练|双创竞赛|学科竞赛/;

  const fileInput = document.querySelector('#csv-file');
  const dropZone = document.querySelector('#drop-zone');
  const output = document.querySelector('#output');

  fileInput.addEventListener('change', () => {
    const [file] = fileInput.files;
    if (file) readFile(file);
  });

  for (const eventName of ['dragenter', 'dragover']) {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.add('dragging');
    });
  }
  for (const eventName of ['dragleave', 'drop']) {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.remove('dragging');
    });
  }
  dropZone.addEventListener('drop', (event) => {
    const [file] = event.dataTransfer.files;
    if (file) readFile(file);
  });

  async function readFile(file) {
    try {
      const data = parseExportCsv(await file.text());
      renderResult(file.name, analyze(data));
    } catch (error) {
      renderError(error instanceof Error ? error.message : String(error));
    }
  }

  function parseExportCsv(text) {
    const grid = parseCsv(text.replace(/^\uFEFF/, ''));
    if (grid.length < 2) throw new Error('CSV 中没有课程记录。');

    const courseHeaderIndex = grid.findIndex((cells) => {
      const headers = cells.map(cleanText);
      return REQUIRED_HEADERS.every((header) => headers.includes(header));
    });
    if (courseHeaderIndex < 0) {
      throw new Error(`CSV 缺少必要列：${REQUIRED_HEADERS.join('、')}。请使用本仓库的导出脚本重新导出。`);
    }

    const innovationHeaderIndex = grid.findIndex((cells) => {
      const headers = cells.map(cleanText);
      return INNOVATION_REQUIRED_HEADERS.every((header) => headers.includes(header));
    });
    const courseHeaders = grid[courseHeaderIndex].map(cleanText);
    const courseEndIndex = innovationHeaderIndex > courseHeaderIndex
      ? innovationHeaderIndex - 1
      : grid.length;
    const courses = grid.slice(courseHeaderIndex + 1, courseEndIndex)
      .filter((cells) => cells.some((cell) => cleanText(cell) !== ''))
      .map((cells, index) => {
        const row = Object.fromEntries(courseHeaders.map(
          (header, column) => [header, cleanText(cells[column])],
        ));
        const credits = Number(row.学分);
        if (!row.课程编号 || !row.课程名称 || !Number.isFinite(credits) || credits < 0) {
          throw new Error(`CSV 第 ${courseHeaderIndex + index + 2} 行的课程编号、课程名称或学分无效。`);
        }
        return { ...row, credits, state: completionState(row.完成情况) };
      });

    const innovationCredits = [];
    const ignoredInnovationCredits = [];
    if (innovationHeaderIndex >= 0) {
      const innovationHeaders = grid[innovationHeaderIndex].map(cleanText);
      const innovationEndIndex = grid.findIndex((cells, index) =>
        index > innovationHeaderIndex && cleanText(cells[0]) === '创新学分汇总');
      const detailRows = grid.slice(
        innovationHeaderIndex + 1,
        innovationEndIndex > innovationHeaderIndex ? innovationEndIndex : grid.length,
      );

      for (const cells of detailRows) {
        if (!/^\d+$/.test(cleanText(cells[0]))) continue;
        const row = Object.fromEntries(innovationHeaders.map(
          (header, column) => [header, cleanText(cells[column])],
        ));
        const credits = Number(row.学分);
        if (!row.级别 || !row.创新学分类别 || !row['项目/课程名称'] ||
            !Number.isFinite(credits) || credits < 0) {
          throw new Error(`创新学分明细第 ${row.序号 || '?'} 条的级别、类别、名称或学分无效。`);
        }
        const innovationCredit = { ...row, credits };
        if (isInnovationCreditEarned(innovationCredit)) {
          innovationCredits.push(innovationCredit);
        } else {
          ignoredInnovationCredits.push(innovationCredit);
        }
      }
    }

    return {
      courses,
      innovationCredits,
      ignoredInnovationCredits,
      hasInnovationSection: innovationHeaderIndex >= 0,
    };
  }

  function parseCsv(text) {
    const rows = [];
    let row = [];
    let cell = '';
    let quoted = false;

    for (let index = 0; index < text.length; index += 1) {
      const character = text[index];
      if (quoted) {
        if (character === '"' && text[index + 1] === '"') {
          cell += '"';
          index += 1;
        } else if (character === '"') {
          quoted = false;
        } else {
          cell += character;
        }
      } else if (character === '"') {
        quoted = true;
      } else if (character === ',') {
        row.push(cell);
        cell = '';
      } else if (character === '\n') {
        row.push(cell.replace(/\r$/, ''));
        rows.push(row);
        row = [];
        cell = '';
      } else {
        cell += character;
      }
    }

    if (quoted) throw new Error('CSV 中存在未闭合的双引号。');
    if (cell !== '' || row.length > 0) {
      row.push(cell.replace(/\r$/, ''));
      rows.push(row);
    }
    return rows;
  }

  function completionState(value) {
    const text = cleanText(value);
    if (/未修读|不及格|未通过|缺考|取消|缓考/.test(text)) return 'ignored';
    if (text.includes('修读中')) return 'ongoing';
    if (/已修|已完成|通过|合格|及格|优|良|中/.test(text)) {
      const numericGrade = text.match(/(?:已修|已完成)\D*(\d+(?:\.\d+)?)/)?.[1];
      return numericGrade !== undefined && Number(numericGrade) < 60 ? 'ignored' : 'completed';
    }
    return 'ignored';
  }

  function isInnovationCreditEarned(row) {
    if (row.credits <= 0 || /不及格|未通过|缺考|取消|缓考/.test(row.成绩)) return false;
    const numericGrade = row.成绩.match(/\d+(?:\.\d+)?/)?.[0];
    return numericGrade === undefined || Number(numericGrade) >= 60;
  }

  function analyze(data) {
    const sourceRows = data.courses;
    const duplicates = new Map();
    for (const row of sourceRows) {
      const existing = duplicates.get(row.课程编号);
      if (!existing || stateRank(row.state) > stateRank(existing.state) ||
          (stateRank(row.state) === stateRank(existing.state) && row.credits > existing.credits)) {
        duplicates.set(row.课程编号, row);
      }
    }

    const rows = [...duplicates.values()];
    const ignored = rows.filter((row) => row.state === 'ignored');
    const completed = rows.filter((row) => row.state === 'completed');
    const projected = rows.filter((row) => row.state === 'completed' || row.state === 'ongoing');
    return {
      duplicateCount: sourceRows.length - rows.length,
      ignored,
      ignoredInnovationCredits: data.ignoredInnovationCredits,
      hasInnovationSection: data.hasInnovationSection,
      completed: evaluate(completed, data.innovationCredits, data.hasInnovationSection),
      projected: evaluate(projected, data.innovationCredits, data.hasInnovationSection),
    };
  }

  function evaluate(rows, innovationRows, hasInnovationSection) {
    const excludedPlanCourses = rows.filter((row) => row.课程体系.includes('计划外'));
    const planRows = rows.filter((row) => !row.课程体系.includes('计划外'));
    const byCode = new Map(planRows.map((row) => [row.课程编号, row]));
    const has = (code) => byCode.has(code);
    const creditsFor = (codes) => sum(codes.map((code) => byCode.get(code)?.credits || 0));
    const rowsFor = (codes) => codes.map((code) => byCode.get(code)).filter(Boolean);
    const missingNames = (courses) => Object.entries(courses)
      .filter(([code]) => !has(code))
      .map(([, name]) => name);
    const checks = [];
    const add = (section, label, passed, detail) => checks.push({ section, label, passed, detail });

    const innovation = classifyInnovation(innovationRows, hasInnovationSection);
    const totalCredits = sum(planRows.map((row) => row.credits)) + innovation.countedCredits;
    const innovationMissingDetail = 'CSV 未包含“创新学分明细”，请使用新版导出脚本重新导出';

    const politicsMissing = missingNames(COURSES.politicsRequired);
    add('通识教育', '思想政治理论必修 15 学分', politicsMissing.length === 0,
      politicsMissing.length ? `缺：${politicsMissing.join('、')}` : '全部完成');

    const historyRows = rowsFor(Object.keys(COURSES.history));
    add('通识教育', '“四史”课程四选一，至少 2 学分', sum(historyRows.map((row) => row.credits)) >= 2,
      progress(sum(historyRows.map((row) => row.credits)), 2));

    const englishRows = planRows.filter((row) => row.课程体系 === '英语' || row.课程编号.startsWith('331'));
    const englishRequired = sum(englishRows.filter((row) => row.课程属性 === '必修').map((row) => row.credits));
    const englishElective = sum(englishRows.filter((row) => row.课程属性 !== '必修').map((row) => row.credits));
    add('通识教育', '英语必修 6 学分', englishRequired >= 6, progress(englishRequired, 6));
    add('通识教育', '英语限定选修 2 学分', englishElective >= 2, progress(englishElective, 2));

    const generalMissing = missingNames(COURSES.generalRequired);
    add('通识教育', '体育基础、军事理论、心理健康、安全教育及两门学院指选课', generalMissing.length === 0,
      generalMissing.length ? `缺：${generalMissing.join('、')}` : '全部完成');

    const sportsCredits = sum(planRows.filter((row) => /^381215\d+$/.test(row.课程编号) && row.课程编号 !== '3812150010')
      .map((row) => row.credits));
    add('通识教育', '体育专项课至少 3 学分', sportsCredits >= 3, progress(sportsCredits, 3));

    const humanitiesCredits = sum(planRows.filter((row) => row.通选课类别 === '人文社科类').map((row) => row.credits));
    const artsCredits = sum(planRows.filter((row) => /美育|艺术/.test(row.通选课类别)).map((row) => row.credits));
    add('通识教育', '人文社科类通选课至少 2 学分', humanitiesCredits >= 2, progress(humanitiesCredits, 2));
    add('通识教育', '美育（CSV 中可能标为“艺术类”）至少 2 学分', artsCredits >= 2, progress(artsCredits, 2));

    const completeCalculus = CALCULUS_GROUPS.some((group) => group.every(has));
    add('数学与自然科学', '高等数学 A（上、下）或数学分析（上、下），两组选一', completeCalculus,
      completeCalculus ? '已完成一组' : '尚无完整的一组');
    const mathMissing = missingNames(COURSES.mathRequired);
    add('数学与自然科学', '线性代数、大学物理 C', mathMissing.length === 0,
      mathMissing.length ? `缺：${mathMissing.join('、')}` : '全部完成');
    add('数学与自然科学', '概率课程二选一，至少 4 学分', creditsFor(PROBABILITY) >= 4,
      progress(creditsFor(PROBABILITY), 4));
    add('数学与自然科学', '组合数学/运筹学/数学建模与模拟/矩阵理论与方法四选一', rowsFor(MATH_ELECTIVE).length >= 1,
      `${rowsFor(MATH_ELECTIVE).length} / 1 门`);

    const disciplineMissing = missingNames(COURSES.discipline);
    add('学科基础', '6 门学科基础必修课，共 17.5 学分', disciplineMissing.length === 0 && creditsFor(Object.keys(COURSES.discipline)) >= 17.5,
      disciplineMissing.length ? `缺：${disciplineMissing.join('、')}` : progress(creditsFor(Object.keys(COURSES.discipline)), 17.5));

    const foundationMissing = missingNames(COURSES.professionalFoundation);
    add('专业基础', '11 门专业基础必修课，共 35 学分', foundationMissing.length === 0 && creditsFor(Object.keys(COURSES.professionalFoundation)) >= 35,
      foundationMissing.length ? `缺：${foundationMissing.join('、')}` : progress(creditsFor(Object.keys(COURSES.professionalFoundation)), 35));

    const professionalRows = planRows.filter((row) => ALL_PROFESSIONAL_ELECTIVES.has(row.课程编号));
    const outsideProfessional = planRows.filter((row) =>
      row.课程体系 === '专业课' && row.课程属性 !== '必修' &&
      !ALL_PROFESSIONAL_ELECTIVES.has(row.课程编号) && !ALL_FIXED_CODES.has(row.课程编号));
    const outsideCredits = Math.min(sum(outsideProfessional.map((row) => row.credits)), 4);
    const professionalCredits = sum(professionalRows.map((row) => row.credits)) + outsideCredits;
    add('专业选修', '专业课至少 16 学分（其他本院专业模块最多计 4 学分）', professionalCredits >= 16,
      `${progress(professionalCredits, 16)}${outsideCredits ? `；含其他本院专业模块 ${formatNumber(outsideCredits)} 学分` : ''}`);
    add('专业选修', '网络与开发技术模块至少 2 门', rowsFor([...PROFESSIONAL_MODULES.network]).length >= 2,
      `${rowsFor([...PROFESSIONAL_MODULES.network]).length} / 2 门`);
    add('专业选修', '大数据技术模块至少 1 门', rowsFor([...PROFESSIONAL_MODULES.data]).length >= 1,
      `${rowsFor([...PROFESSIONAL_MODULES.data]).length} / 1 门`);
    add('专业选修', '技术拓展模块至少 1 门', rowsFor([...PROFESSIONAL_MODULES.extension]).length >= 1,
      `${rowsFor([...PROFESSIONAL_MODULES.extension]).length} / 1 门`);

    const practiceMissing = missingNames(COURSES.practiceRequired);
    const labor = planRows.find((row) => normalizeName(row.课程名称) === '劳动教育');
    const requiredPracticeCredits = creditsFor(Object.keys(COURSES.practiceRequired)) + (labor?.credits || 0);
    add('实践教学', '必修实践课程，共 18 学分', practiceMissing.length === 0 && Boolean(labor) && requiredPracticeCredits >= 18,
      practiceMissing.length || !labor
        ? `缺：${[...practiceMissing, ...(!labor ? ['劳动教育'] : [])].join('、')}`
        : progress(requiredPracticeCredits, 18));

    for (const group of PRACTICE_GROUPS) {
      const count = rowsFor(group.codes).length;
      add('实践教学', group.label, count >= group.count, `${count} / ${group.count} 门`);
    }
    add('实践教学', '专业实习（指选）1.5 学分', has('3132102131'), has('3132102131') ? '已完成' : '缺：专业实习');

    const practiceElectiveCredits = sum(PRACTICE_GROUPS.map((group) =>
      sum(rowsFor(group.codes).map((row) => row.credits).sort((a, b) => b - a).slice(0, group.count)))) +
      (byCode.get('3132102131')?.credits || 0);
    add('实践教学', '实践教学最低选修 11.5 学分', practiceElectiveCredits >= 11.5,
      progress(practiceElectiveCredits, 11.5));

    add('创新创业', '校级创新创业教育至少 3 学分', innovation.schoolCredits >= 3,
      hasInnovationSection ? progress(innovation.schoolCredits, 3) : innovationMissingDetail);
    add('创新创业', '校级创新创业实践至少 2 学分', innovation.schoolPracticeCredits >= 2,
      hasInnovationSection ? progress(innovation.schoolPracticeCredits, 2) : innovationMissingDetail);
    add('创新创业', '院级“创新创业实践课”指选 1.5 学分', innovation.collegeFixedCompleted,
      !hasInnovationSection
        ? innovationMissingDetail
        : innovation.collegeFixedCompleted ? '已完成' : '缺：创新创业实践课（现代信息技术创新与实践）');
    add('创新创业', '院级实践训练/科研训练/竞赛至少 2 学分', innovation.collegePracticeCredits >= 2,
      hasInnovationSection ? progress(innovation.collegePracticeCredits, 2) : innovationMissingDetail);

    add('总学分', '培养方案内课程总学分至少 165', totalCredits >= 165, progress(totalCredits, 165));

    return {
      passed: checks.every((check) => check.passed),
      checks,
      totalCredits,
      courseCount: planRows.length,
      excludedPlanCourses,
      outsideProfessional,
      innovation,
    };
  }

  function classifyInnovation(rows, hasInnovationSection) {
    const schoolRows = rows.filter((row) => row.级别.includes('校级'));
    const collegeRows = rows.filter((row) => row.级别.includes('院级'));
    const collegeFixed = collegeRows.find((row) =>
      COLLEGE_FIXED_PATTERN.test(`${row.创新学分类别} ${row['项目/课程名称']}`));
    const collegePracticeRows = collegeRows.filter((row) =>
      row !== collegeFixed &&
      COLLEGE_PRACTICE_PATTERN.test(`${row.创新学分类别} ${row['项目/课程名称']}`));
    const schoolCredits = sum(schoolRows.map((row) => row.credits));
    const schoolPracticeCredits = sum(schoolRows
      .filter((row) => /实践/.test(`${row.级别} ${row.创新学分类别}`))
      .map((row) => row.credits));
    const collegePracticeCredits = sum(collegePracticeRows.map((row) => row.credits));
    const collegeCredits = (collegeFixed?.credits || 0) + collegePracticeCredits;
    const unclassifiedRows = rows.filter((row) =>
      !schoolRows.includes(row) && row !== collegeFixed && !collegePracticeRows.includes(row));

    return {
      hasInnovationSection,
      recordCount: rows.length,
      schoolCredits,
      schoolPracticeCredits,
      collegeFixedCompleted: Boolean(collegeFixed && collegeFixed.credits >= 1.5),
      collegePracticeCredits,
      countedCredits: Math.min(schoolCredits, 3) + Math.min(collegeCredits, 3.5),
      unclassifiedRows,
    };
  }

  function renderResult(fileName, result) {
    const currentFailures = result.completed.checks.filter((check) => !check.passed).length;
    const projectedFailures = result.projected.checks.filter((check) => !check.passed).length;
    const sections = [...new Set(result.completed.checks.map((check) => check.section))];

    output.innerHTML = `
      <section class="summary" aria-live="polite">
        <div>
          <p class="eyebrow">${escapeHtml(fileName)}</p>
          <h2>${result.completed.passed ? '当前已满足毕业课程要求' : `当前还有 ${currentFailures} 项未满足`}</h2>
          <p>按课程编号去重并排除计划外课程后，已修 ${result.completed.courseCount} 门；创新创业按培养方案计入 ${formatNumber(result.completed.innovation.countedCredits)} / 6.5 学分。当前合计 ${formatNumber(result.completed.totalCredits)} 学分，含修读中预计 ${formatNumber(result.projected.totalCredits)} 学分。</p>
        </div>
        <div class="verdicts">
          ${verdict('仅已修', result.completed.passed, currentFailures)}
          ${verdict('含修读中', result.projected.passed, projectedFailures)}
        </div>
      </section>
      <p class="scope-note">结论覆盖 2023 版计算机科学与技术专业的课程、学分和选课组合要求；培养方案中的能力指标、体测、处分及学位授予等非 CSV 信息不在自动判定范围内。</p>
      ${sections.map((section) => renderSection(section, result.completed, result.projected)).join('')}
      ${renderNotes(result)}
    `;
  }

  function renderSection(section, completed, projected) {
    const currentChecks = completed.checks.filter((check) => check.section === section);
    const projectedByLabel = new Map(projected.checks.filter((check) => check.section === section)
      .map((check) => [check.label, check]));

    return `
      <section class="check-section">
        <h3>${escapeHtml(section)}</h3>
        <div class="check-list">
          ${currentChecks.map((current) => {
            const future = projectedByLabel.get(current.label);
            return `
              <div class="check-row">
                <div>
                  <strong>${escapeHtml(current.label)}</strong>
                  <span>${escapeHtml(current.detail)}</span>
                </div>
                <div class="check-states">
                  ${stateBadge('已修', current.passed)}
                  ${stateBadge('含在修', future.passed)}
                </div>
              </div>`;
          }).join('')}
        </div>
      </section>`;
  }

  function renderNotes(result) {
    const notes = [];
    if (result.duplicateCount > 0) {
      notes.push(`发现 ${result.duplicateCount} 条同课程编号的重复记录，已只保留状态优先、学分最高的一条，避免体育和英语重复计分。`);
    }
    if (result.ignored.length > 0) {
      notes.push(`有 ${result.ignored.length} 门课程因未修读、未通过或状态无法识别而未计入。`);
    }
    if (result.ignoredInnovationCredits.length > 0) {
      notes.push(`有 ${result.ignoredInnovationCredits.length} 条创新学分记录因学分为 0、未通过或成绩低于 60 分而未计入。`);
    }
    if (result.projected.excludedPlanCourses.length > 0) {
      notes.push(`“计划外课程”共 ${formatNumber(sum(result.projected.excludedPlanCourses.map((row) => row.credits)))} 学分，未计入 165 学分。`);
    }
    if (result.projected.outsideProfessional.length > 0) {
      notes.push(`将 ${result.projected.outsideProfessional.map((row) => row.课程名称).join('、')} 识别为其他本院专业模块课，按方案最多计 4 学分；请与最终教务认定核对。`);
    }
    if (!result.hasInnovationSection) {
      notes.push('当前文件没有“创新学分明细”区段，双创要求无法证明并按缺项处理；请使用新版导出脚本生成合并 CSV。');
    } else {
      notes.push(`已读取 ${result.completed.innovation.recordCount} 条有效创新学分记录；校级最多计 3 学分、院级最多计 3.5 学分。CSV 中的“创新学分汇总”仅供核对，自动判定以逐条明细为准。`);
    }
    if (result.completed.innovation.unclassifiedRows.length > 0) {
      notes.push(`以下创新学分记录不符合培养方案中的校级或院级可计入类型，未计入：${result.completed.innovation.unclassifiedRows.map((row) => row['项目/课程名称']).join('、')}。`);
    }

    return `<section class="notes"><h3>判定说明</h3><ul>${notes.map((note) => `<li>${escapeHtml(note)}</li>`).join('')}</ul></section>`;
  }

  function verdict(label, passed, failures) {
    return `<div class="verdict ${passed ? 'pass' : 'fail'}"><span>${escapeHtml(label)}</span><strong>${passed ? '满足' : `缺 ${failures} 项`}</strong></div>`;
  }

  function stateBadge(label, passed) {
    return `<span class="badge ${passed ? 'pass' : 'fail'}">${passed ? '✓' : '×'} ${escapeHtml(label)}</span>`;
  }

  function renderError(message) {
    output.innerHTML = `<section class="error" role="alert"><h2>无法校验这个文件</h2><p>${escapeHtml(message)}</p></section>`;
  }

  function cleanText(value) {
    return String(value ?? '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
  }

  function normalizeName(value) {
    return cleanText(value).replace(/[（）()\s]/g, '').replace(/[Ａ-Ｚａ-ｚ０-９]/g, (character) =>
      String.fromCharCode(character.charCodeAt(0) - 0xFEE0));
  }

  function stateRank(state) {
    return { ignored: 0, ongoing: 1, completed: 2 }[state] || 0;
  }

  function sum(values) {
    return values.reduce((total, value) => total + value, 0);
  }

  function progress(actual, required) {
    return `${formatNumber(actual)} / ${formatNumber(required)} 学分`;
  }

  function formatNumber(value) {
    return Number(value.toFixed(2)).toString();
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (character) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
    })[character]);
  }
})();
