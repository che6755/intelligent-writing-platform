<template>
  <div class="guide-page">
    <nav class="guide-nav">
      <button type="button" class="back-btn" title="返回首页" @click="$router.push('/')">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
      </button>
      <span>使用说明</span>
    </nav>

    <main class="guide-content">
      <header class="guide-hero">
        <p class="eyebrow">智能写作助手</p>
        <h1>从主题到成稿，按需使用 AI</h1>
        <p>平台只提供中文或英文议论文辅助。你可以先独立思考，再在需要时调用对应功能。</p>
      </header>

      <section class="guide-section">
        <div class="section-heading">
          <span class="step-number">01</span>
          <div>
            <h2>开始创作</h2>
            <p>先选择身份和作文语言，再输入题目、主题，或一段较完整的引论。</p>
          </div>
        </div>
        <figure class="guide-shot"><img src="/guide/create.png" alt="创建页身份、语言和主题输入示例" /><figcaption>选择写作者身份和作文语言，再输入主题或题目。</figcaption></figure>
      </section>

      <section class="guide-section">
        <div class="section-heading">
          <span class="step-number">02</span>
          <div>
            <h2>按主题获取写作提示</h2>
            <p>大纲提示和举例提示都根据创建时填写的主题生成，需要时主动点击即可。</p>
          </div>
        </div>
        <div class="feature-grid">
          <article class="feature-card">
            <span class="feature-icon">☷</span>
            <h3>写作结构提示</h3>
            <p>根据作文主题生成议论文结构方向，帮助你梳理中心论点、分论点和论据安排。</p>
          </article>
          <article class="feature-card">
            <span class="feature-icon">✦</span>
            <h3>举例方向提示</h3>
            <p>中文作文可获取案例、事实或名言方向，不直接代写完整段落。</p>
          </article>
          <article class="feature-card">
            <span class="feature-icon">Aa</span>
            <h3>英文写作检查</h3>
            <p>英文作文可以在写作过程中主动检查已写内容的语法；中文作文的检测功能集中在完成后分析。</p>
          </article>
        </div>
        <figure class="guide-shot"><img src="/guide/writing-actions.png" alt="写作页操作按钮示例" /><figcaption>写作中按需使用结构提示、举例提示或完成评分。</figcaption></figure>
      </section>

      <section class="guide-section">
        <div class="section-heading">
          <span class="step-number">03</span>
          <div>
            <h2>完成后分析</h2>
            <p>提交评分后，侧边栏会收起，写作区扩展到整行。你可以按需查看专项分析。</p>
          </div>
        </div>
        <div class="result-list">
          <span>中文：标题优化、全文语法检测、整体逻辑、可用样例、句式润色</span>
          <span>英文：全文语法检测、句式润色、整体结构检查</span>
          <span>评分：内容、结构逻辑、语言表达三个维度</span>
        </div>
        <figure class="guide-shot"><img src="/guide/score-report.png" alt="完成后分析与评分报告示例" /><figcaption>完成评分后查看专项分析和三维评分报告。</figcaption></figure>
      </section>
    </main>
  </div>
</template>

<style scoped>
.guide-page { min-height: 100vh; background: #f5f7fa; color: #27364a; }
.guide-nav { display: flex; align-items: center; gap: 16px; max-width: 1080px; margin: 0 auto; padding: 24px 32px 10px; font-size: 18px; font-weight: 700; }
.back-btn { position: relative; width: 52px; height: 52px; padding: 0; border: 1px solid #dce3ee; border-radius: 12px; background: #fff; color: #52719a; cursor: pointer; transition: background .2s, border-color .2s, transform .2s; }
.back-btn svg { position: absolute; top: 50%; left: 50%; display: block; width: 26px; height: 26px; transform: translate(-50%, -50%); fill: none; stroke: currentColor; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
.back-btn:hover { background: #f1f5ff; border-color: #b9c8ed; transform: translateX(-2px); }
.guide-content { max-width: 1080px; margin: 0 auto; padding: 28px 32px 72px; }
.guide-hero { padding: 44px 48px; border-radius: 18px; background: linear-gradient(135deg, #4b68d8, #7060e9); color: #fff; box-shadow: 0 18px 40px rgba(77, 91, 190, .18); }
.eyebrow { margin: 0 0 10px; opacity: .78; font-size: 13px; letter-spacing: 1px; }
.guide-hero h1 { margin: 0 0 12px; font-size: 34px; }
.guide-hero > p:last-child { max-width: 720px; margin: 0 auto; line-height: 1.8; opacity: .9; text-align: center; }
.guide-section { margin-top: 40px; padding: 30px; border: 1px solid #e2e8f2; border-radius: 16px; background: #fff; }
.section-heading { display: flex; gap: 16px; align-items: flex-start; }
.step-number { color: #5d70dc; font-size: 13px; font-weight: 800; letter-spacing: 1px; }
.section-heading h2 { margin: 0 0 8px; font-size: 23px; }
.section-heading p { margin: 0; color: #718096; line-height: 1.7; }
.mock-screen { margin-top: 24px; border: 1px solid #dfe6f0; border-radius: 12px; background: #f8fafc; overflow: hidden; }
.mock-topbar { display: flex; gap: 6px; padding: 12px 16px; border-bottom: 1px solid #e6ebf2; background: #fff; }
.mock-topbar span { width: 8px; height: 8px; border-radius: 50%; background: #cbd5e1; }
.mock-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; max-width: 680px; margin: 28px auto; padding: 0 24px; }
.mock-select, .mock-input { padding: 14px; border: 1px solid #dbe3ee; border-radius: 8px; background: #fff; color: #66758a; }
.mock-select b { float: right; color: #9aa8b9; }
.mock-input { grid-column: 1 / -1; color: #b0bac8; }
.mock-button { grid-column: 1 / -1; justify-self: center; padding: 12px 64px; border-radius: 8px; background: #6372df; color: #fff; font-weight: 700; }
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 24px; }
.feature-card { padding: 20px; border: 1px solid #e4eaf3; border-radius: 10px; background: #fbfcfe; }
.feature-icon { display: inline-flex; min-width: 28px; color: #5e70d9; font-weight: 800; }
.feature-card h3 { margin: 12px 0 8px; font-size: 17px; }
.feature-card p { margin: 0; color: #718096; line-height: 1.7; font-size: 14px; }
.editor-mock { display: grid; grid-template-columns: 1fr 250px; min-height: 190px; }
.mock-editor-area { padding: 30px; color: #9aa8b9; background: #fff; }
.editor-mock aside { display: grid; align-content: start; gap: 14px; padding: 22px; border-left: 1px solid #e4eaf3; background: #fff; }
.editor-mock aside i { padding: 10px; border-radius: 6px; background: #f2f6ff; color: #60718a; font-style: normal; font-size: 13px; }
.result-list { display: grid; gap: 10px; margin-top: 22px; }
.result-list span { padding: 14px 16px; border-left: 3px solid #6475df; background: #f7f8ff; color: #5d6d83; }
.guide-shot { margin: 24px 0 0; padding: 14px; border: 1px solid #e1e7f0; border-radius: 12px; background: #f8fafc; }
.guide-shot img { display: block; width: 100%; max-height: 520px; object-fit: contain; border-radius: 7px; background: #fff; }
.guide-shot figcaption { padding: 12px 4px 2px; color: #718096; font-size: 14px; text-align: center; }
.history-heading { display: flex; align-items: center; justify-content: space-between; }
.guide-link { padding: 8px 14px; border: 1px solid #d5def0; border-radius: 8px; background: #fff; color: #5268c7; cursor: pointer; }
@media (max-width: 700px) { .guide-content, .guide-nav { padding-left: 18px; padding-right: 18px; } .guide-hero { padding: 30px 24px; } .guide-hero h1 { font-size: 28px; } .feature-grid, .editor-mock { grid-template-columns: 1fr; } .editor-mock aside { border-left: 0; border-top: 1px solid #e4eaf3; } .mock-fields { grid-template-columns: 1fr; } .mock-input, .mock-button { grid-column: auto; } }
</style>
