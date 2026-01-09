(async () => {
  const CONFIG = {
    // 0=完全符合, 1=基本符合, 2=不确定, 3=基本不符合, 4=完全不符合
    // 学校页面会拒绝“所有题目选择同一档”，所以默认第一题选 1，其余题选 0。
    optionPattern: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    positiveTags: [
      "老师认真负责",
      "老师非常有耐心",
      "老师教学水平高",
      "老师思路清晰"
    ],
    improvementText: "课程安排合理，后续可以适当增加课堂互动与案例讲解。",
    highlightText: "老师备课充分，讲解清晰，课程内容充实，能够帮助学生理解重点内容。",
    // 最终提交后页面提示无法修改。确认所有课程保存成功后，再改成 true 运行。
    finalSubmit: false,
    delayMs: 300
  };

  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const docFrom = html => new DOMParser().parseFromString(html, "text/html");
  const absoluteUrl = href => new URL(href, location.origin).href;
  const text = el => (el?.innerText || el?.textContent || "").replace(/\s+/g, " ").trim();

  async function fetchDocument(url, options) {
    const response = await fetch(url, {
      credentials: "same-origin",
      redirect: "follow",
      ...options
    });
    const html = await response.text();
    if (!response.ok) {
      throw new Error(`请求失败: ${response.status} ${response.statusText} ${url}`);
    }
    if (/用户登录|请输入账号|请输入密码/.test(html)) {
      throw new Error("登录状态失效，请重新登录后再次运行。");
    }
    return { response, doc: docFrom(html), html };
  }

  function getCourseLinks(doc) {
    return [...doc.querySelectorAll('a[href*="/jsxsd/xspj/xspj_edit.do"], a[href*="xspj_edit.do"]')]
      .map(a => ({
        href: absoluteUrl(a.getAttribute("href")),
        rowText: text(a.closest("tr"))
      }))
      .filter(item => item.href);
  }

  function fillEvaluationForm(doc, courseIndex) {
    const form = doc.querySelector("form#Form1, form[name='Form1'], form");
    if (!form) throw new Error("评价页未找到表单。");

    const radioNames = [...new Set(
      [...form.querySelectorAll('input[type="radio"][name^="pj0601id_"]')].map(input => input.name)
    )];
    if (radioNames.length === 0) throw new Error("评价页未找到单选题。");

    radioNames.forEach((name, index) => {
      const radios = [...form.querySelectorAll(`input[type="radio"][name="${CSS.escape(name)}"]`)];
      const desired = CONFIG.optionPattern[index % CONFIG.optionPattern.length] ?? 0;
      const radio = radios[Math.min(desired, radios.length - 1)];
      if (!radio) throw new Error(`题目 ${name} 未找到可选项。`);
      radio.checked = true;
    });

    const checks = [...form.querySelectorAll('input[type="checkbox"][name="zgpyids"]')];
    checks.forEach(input => {
      input.checked = CONFIG.positiveTags.some(tag => text(input.closest("td") || input.parentElement).includes(tag));
    });
    if (checks.length > 0 && !checks.some(input => input.checked)) {
      checks.slice(0, 4).forEach(input => input.checked = true);
    }

    const textareas = [...form.querySelectorAll("textarea")];
    if (textareas[0]) textareas[0].value = CONFIG.improvementText;
    if (textareas[1]) textareas[1].value = CONFIG.highlightText;

    const byId = id => form.querySelector(`#${CSS.escape(id)}`);
    if (byId("issubmit")) byId("issubmit").value = "0";
    if (byId("sfxyt")) byId("sfxyt").value = "0";
    if (byId("sava")) byId("sava").value = "0";

    const courseName =
      text(doc.body).match(/课程名称：\s*([^评]+?)\s*评教大类/)?.[1]?.trim()
      || `第 ${courseIndex + 1} 门课程`;

    return { form, courseName };
  }

  async function saveOneCourse(link, index, total) {
    console.log(`[${index + 1}/${total}] 读取: ${link.rowText}`);
    const { doc } = await fetchDocument(link.href);
    const { form, courseName } = fillEvaluationForm(doc, index);
    const formData = new FormData(form);
    const action = absoluteUrl(form.getAttribute("action") || "/jsxsd/xspj/xspj_save.do");

    const response = await fetch(action, {
      method: (form.getAttribute("method") || "POST").toUpperCase(),
      body: formData,
      credentials: "same-origin",
      redirect: "follow"
    });
    const html = await response.text();
    if (!response.ok) {
      throw new Error(`[${courseName}] 保存失败: ${response.status} ${response.statusText}`);
    }
    if (/评价的每项指标都必须选择|请不要选相同一项|请选择主观评语指标|不能为空|请填写意见建议/.test(html)) {
      throw new Error(`[${courseName}] 保存后页面仍包含校验提示，请打开该课程人工检查。`);
    }
    console.log(`[${index + 1}/${total}] 保存完成: ${courseName}`);
    await sleep(CONFIG.delayMs);
  }

  async function submitFinal(listDoc) {
    const form = listDoc.querySelector("form[name='Form1'], form#Form1, form");
    const pj01id = listDoc.querySelector("#pj01id")?.value;
    if (!form || !pj01id) throw new Error("列表页未找到最终提交表单或 pj01id。");
    const action = absoluteUrl(`/jsxsd/xspj/xspj_yjtj.do?pj01id=${encodeURIComponent(pj01id)}`);
    const response = await fetch(action, {
      method: "POST",
      body: new FormData(form),
      credentials: "same-origin",
      redirect: "follow"
    });
    if (!response.ok) {
      throw new Error(`最终提交失败: ${response.status} ${response.statusText}`);
    }
    console.log("最终提交请求完成。");
  }

  try {
    console.log("开始读取课程列表...");
    const listUrl = location.href.includes("/jsxsd/xspj/xspj_list.do")
      ? location.href
      : absoluteUrl("/jsxsd/xspj/xspj_list.do?pj0502id=F3FA95DA7F19467DB90F098784CC2DCE&pj01id=&xnxq01id=2025-2026-2");

    let { doc: listDoc } = await fetchDocument(listUrl);
    let links = getCourseLinks(listDoc);
    if (links.length === 0) {
      throw new Error("未找到待评价课程链接。请先进入“学生评价”的课程列表页后再次运行。");
    }

    for (let i = 0; i < links.length; i += 1) {
      await saveOneCourse(links[i], i, links.length);
    }

    ({ doc: listDoc } = await fetchDocument(listUrl));
    const afterText = text(listDoc.body);
    console.log("保存后列表摘要:", afterText.match(/共\d+页\s*\d+条/)?.[0] || "列表读取完成");

    if (CONFIG.finalSubmit) {
      await submitFinal(listDoc);
    } else {
      console.log("所有课程保存流程完成。最终“提 交”未执行；确认列表显示全部已评后，可将 CONFIG.finalSubmit 改为 true 再运行。");
    }
  } catch (error) {
    console.error(error);
    alert(`自动填写中断：${error.message}`);
  }
})();
