(async () => {
  'use strict';

  const COURSE_HEADERS = [
    '课程体系', '课程编号', '课程名称', '完成情况', '课程性质', '课程属性', '学分',
    '讲课学时', '实践学时', '讲座学时', '实验学时', '课外学时', '总学时',
    '通选课类别', '开设学期',
  ];
  const COURSE_REQUIRED_HEADERS = ['课程编号', '课程名称', '完成情况', '课程属性', '学分'];
  const INNOVATION_HEADERS = [
    '序号', '学年学期', '级别', '创新学分类别', '项目/课程名称', '学分', '成绩',
  ];
  const INNOVATION_REQUIRED_HEADERS = [
    '学年学期', '级别', '创新学分类别', '项目/课程名称', '学分', '成绩',
  ];

  function cleanText(value) {
    return String(value ?? '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
  }

  function getSameOriginDocuments(rootDocument) {
    const documents = [rootDocument];

    for (const frame of rootDocument.querySelectorAll('iframe, frame')) {
      try {
        if (!frame.contentDocument || frame.contentDocument === rootDocument) continue;
        documents.push(...getSameOriginDocuments(frame.contentDocument));
      } catch {
        // WebVPN 外的跨域 iframe 不在导出范围内。
      }
    }

    return documents;
  }

  function findTable(requiredHeaders) {
    for (const currentDocument of getSameOriginDocuments(document)) {
      const table = Array.from(currentDocument.querySelectorAll('table')).find((candidate) => {
        const firstRowText = cleanText(candidate.rows[0]?.innerText);
        return requiredHeaders.every((header) => firstRowText.includes(header));
      });
      if (table) return table;
    }

    return null;
  }

  function tableToGrid(table) {
    const spans = [];

    return Array.from(table.rows).map((tableRow) => {
      const row = [];

      for (let column = 0; column < spans.length; column += 1) {
        const span = spans[column];
        if (!span) continue;
        row[column] = span.value;
        span.rowsLeft -= 1;
        if (span.rowsLeft === 0) spans[column] = null;
      }

      let column = 0;
      for (const cell of tableRow.cells) {
        while (row[column] !== undefined) column += 1;

        const value = cleanText(cell.innerText);
        const columnSpan = Math.max(cell.colSpan || 1, 1);
        const rowSpan = Math.max(cell.rowSpan || 1, 1);

        for (let offset = 0; offset < columnSpan; offset += 1) {
          row[column + offset] = value;
          if (rowSpan > 1) {
            spans[column + offset] = { value, rowsLeft: rowSpan - 1 };
          }
        }
        column += columnSpan;
      }

      return row;
    });
  }

  function extractTakenCourses(table) {
    return tableToGrid(table)
      .filter((row) => {
        const courseCode = row[1] || '';
        const completion = row[3] || '';
        const looksLikeCourseCode = /^(?=.*[A-Za-z0-9])[A-Za-z0-9._-]{6,}$/.test(courseCode);
        return looksLikeCourseCode && completion !== '' && !completion.includes('未修读');
      })
      .map((row) => COURSE_HEADERS.map((_, index) => row[index] || ''));
  }

  function extractInnovationCredits(table) {
    const detailRows = [];
    const summaryRows = [];

    for (const tableRow of Array.from(table.rows).slice(1)) {
      const cells = Array.from(tableRow.cells).map((cell) => cleanText(cell.innerText));
      if (cells[0] === '汇总：' || cells[0] === '汇总:') {
        const summaryCell = tableRow.cells[1];
        const lines = Array.from(summaryCell?.querySelectorAll('div, p, li') || [])
          .map((element) => cleanText(element.innerText))
          .filter(Boolean);
        summaryRows.push(...(lines.length > 0 ? lines : [cleanText(summaryCell?.innerText)]));
        continue;
      }

      if (/^\d+$/.test(cells[0] || '')) {
        detailRows.push(INNOVATION_HEADERS.map((_, index) => cells[index] || ''));
      }
    }

    return { detailRows, summaryRows: summaryRows.filter(Boolean) };
  }

  function isVisible(element) {
    const style = element.ownerDocument.defaultView?.getComputedStyle(element);
    return style?.display !== 'none' && style?.visibility !== 'hidden';
  }

  function navigateTo(label) {
    const candidates = Array.from(document.querySelectorAll('a, button, [onclick], li, div, span'))
      .filter((element) => cleanText(element.innerText || element.textContent) === label)
      .filter(isVisible);
    const target = candidates.find((element) => element.matches('a, button, [onclick]'))
      || candidates[0];

    if (!target) {
      throw new Error(`未找到“${label}”入口，请从本科教务系统首页运行脚本。`);
    }
    target.click();
  }

  async function waitForTable(requiredHeaders, timeoutMs = 20_000) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const table = findTable(requiredHeaders);
      if (table) return table;
      await new Promise((resolve) => window.setTimeout(resolve, 200));
    }
    return null;
  }

  async function loadTable(label, requiredHeaders) {
    const existingTable = findTable(requiredHeaders);
    if (existingTable) return existingTable;

    navigateTo(label);
    const table = await waitForTable(requiredHeaders);
    if (!table) throw new Error(`“${label}”页面加载超时，请刷新教务系统后重试。`);
    return table;
  }

  function escapeCsvCell(value) {
    let text = cleanText(value);
    if (/^[=+\-@]/.test(text)) text = `'${text}`;
    return `"${text.replace(/"/g, '""')}"`;
  }

  function createLocalDate() {
    const now = new Date();
    return [
      now.getFullYear(),
      String(now.getMonth() + 1).padStart(2, '0'),
      String(now.getDate()).padStart(2, '0'),
    ].join('-');
  }

  function downloadCsv(courses, innovation) {
    const rows = [
      ['所修课程'],
      COURSE_HEADERS,
      ...courses,
      [],
      ['创新学分明细'],
      INNOVATION_HEADERS,
      ...innovation.detailRows,
      [],
      ['创新学分汇总'],
      ['汇总内容'],
      ...innovation.summaryRows.map((summary) => [summary]),
    ];
    const csv = rows.map((row) => row.map(escapeCsvCell).join(',')).join('\r\n');
    const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = `北邮培养方案与创新学分_${createLocalDate()}.csv`;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  const initialPage = findTable(COURSE_REQUIRED_HEADERS)
    ? '培养方案完成情况'
    : findTable(INNOVATION_REQUIRED_HEADERS)
      ? '创新学分查询'
      : null;

  try {
    console.info('正在读取培养方案完成情况……');
    const courseTable = await loadTable('培养方案完成情况', COURSE_REQUIRED_HEADERS);
    const courses = extractTakenCourses(courseTable);

    console.info('正在读取创新学分查询……');
    const innovationTable = await loadTable('创新学分查询', INNOVATION_REQUIRED_HEADERS);
    const innovation = extractInnovationCredits(innovationTable);

    if (courses.length === 0) throw new Error('没有找到已修或修读中的课程。');
    downloadCsv(courses, innovation);
    console.info(`导出完成：${courses.length} 门课程，${innovation.detailRows.length} 条创新学分记录。`);
  } catch (error) {
    console.error(error instanceof Error ? error.message : error);
  } finally {
    const initialHeaders = initialPage === '培养方案完成情况'
      ? COURSE_REQUIRED_HEADERS
      : INNOVATION_REQUIRED_HEADERS;
    if (initialPage && !findTable(initialHeaders)) navigateTo(initialPage);
  }
})();
