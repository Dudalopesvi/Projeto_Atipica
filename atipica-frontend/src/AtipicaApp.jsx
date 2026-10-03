import React, { useEffect, useId, useRef, useState } from "react";
import {
  Activity,
  BookOpen,
  Bot,
  RotateCcw,
  Check,
  ChevronDown,
  Heart,
  Home,
  LogOut,
  MessageCircle,
  Printer,
  Search,
  Send,
  ShieldCheck,
  Settings,
  UserRound,
  Users,
  X,
} from "lucide-react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const COLORS = {
  primary: "#7d2844",
  ink: "#24303a",
  muted: "#60707b",
};

let currentEmail = null;

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || `Falha na comunicação com ${path}`);
  }
  return body;
}

const get = (path) => api(path);
const post = (path, body) => api(path, { method: "POST", body: JSON.stringify(body) });
const patch = (path, body) => api(path, { method: "PATCH", body: JSON.stringify(body) });

function Button({ children, secondary = false, type = "button", onClick, disabled = false, icon: Icon, className = "", ...props }) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`btn ${secondary ? "btn-secondary" : "btn-primary"} ${className}`.trim()}
      {...props}
    >
      {Icon && <Icon size={17} aria-hidden="true" />}
      {children}
    </button>
  );
}

function Field({ label, value, onChange, multiline = false, hint, id, ...props }) {
  const generatedId = useId();
  const inputId = id || `field-${generatedId}`;
  const hintId = hint ? `${inputId}-hint` : undefined;
  const Tag = multiline ? "textarea" : "input";

  return (
    <label className="field" htmlFor={inputId}>
      <span>{label}</span>
      {hint && <small id={hintId} className="field-hint">{hint}</small>}
      <Tag
        id={inputId}
        value={value ?? ""}
        onChange={onChange}
        aria-describedby={hintId}
        {...props}
      />
    </label>
  );
}

function Card({ children, className = "", as: Tag = "section", ...props }) {
  return <Tag className={`card ${className}`.trim()} {...props}>{children}</Tag>;
}

function Empty({ children }) {
  return <p className="empty" role="status">{children}</p>;
}

function TabCard({ icon: Icon, label, title, description, indicator, tone = "blue", active = false, onClick }) {
  return (
    <button type="button" className={`tab-card tab-card-${tone} ${active ? "active" : ""}`} onClick={onClick} aria-current={active ? "page" : undefined}>
      <span className="tab-card-icon" aria-hidden="true"><Icon size={22} /></span>
      <span className="tab-card-label">{label}</span>
      <strong>{title}</strong>
      <span className="tab-card-description">{description}</span>
      <span className="tab-card-footer"><span className="tab-card-indicator"><span aria-hidden="true" />{indicator}</span><span className="tab-card-action">Acessar <span aria-hidden="true">→</span></span></span>
    </button>
  );
}

function LoginView({ onSuccess }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    nome: "",
    nome_crianca: "",
    email: "",
    senha: "",
    idade_crianca: "",
    comunicacao_crianca: "",
    necessidades_crianca: "",
    interesses_crianca: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const set = (key) => (event) => setForm((old) => ({ ...old, [key]: event.target.value }));

  function changeMode(nextMode) {
    setMode(nextMode);
    setError("");
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const profile = await post(
        `/api/${mode === "login" ? "login" : "cadastro"}`,
        mode === "login" ? { email: form.email, senha: form.senha } : form,
      );
      onSuccess(profile);
    } catch (e) {
      setError(e.message || "Não foi possível concluir a operação.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={submit} aria-labelledby="auth-title">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">A</div>
          <div>
            <h1 id="auth-title">Atípica</h1>
            <p>Rotina, cuidado e informação com clareza.</p>
          </div>
        </div>

        <p className="auth-intro">Um espaço para organizar o dia de quem vive o TEA e de quem oferece apoio.</p>

        <div className="switcher" role="tablist" aria-label="Acesso ao Atípica">
          <button
            type="button"
            role="tab"
            aria-selected={mode === "login"}
            className={mode === "login" ? "selected" : ""}
            onClick={() => changeMode("login")}
          >
            Entrar
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === "cadastro"}
            className={mode === "cadastro" ? "selected" : ""}
            onClick={() => changeMode("cadastro")}
          >
            Criar perfil
          </button>
        </div>

        {mode === "cadastro" && (
          <div className="profile-onboarding">
            <p className="form-section-title">Primeiro, conte só o que for confortável.</p>
            <Field label="Nome de quem usa o perfil" value={form.nome} onChange={set("nome")} required placeholder="Como devemos chamar você?" autoComplete="name" />
            <Field label="Nome da pessoa acompanhada" value={form.nome_crianca} onChange={set("nome_crianca")} required placeholder="Pode ser seu nome ou de alguém da família" />
            <div className="two-col">
              <Field label="Idade" value={form.idade_crianca} onChange={set("idade_crianca")} placeholder="Ex.: 8 anos" />
              <Field label="Comunicação" value={form.comunicacao_crianca} onChange={set("comunicacao_crianca")} placeholder="Ex.: fala, CAA..." />
            </div>
            <Field label="Necessidades de apoio" value={form.necessidades_crianca} onChange={set("necessidades_crianca")} multiline placeholder="Conte o que é importante para a rotina." />
            <Field label="Interesses" value={form.interesses_crianca} onChange={set("interesses_crianca")} multiline placeholder="Atividades, temas ou objetos de interesse." />
          </div>
        )}

        <Field label="E-mail" value={form.email} onChange={set("email")} type="email" required placeholder="seu@email.com" autoComplete="email" />
        <Field label="Senha" value={form.senha} onChange={set("senha")} type="password" minLength={mode === "cadastro" ? 6 : undefined} required placeholder="Mínimo de 6 caracteres" autoComplete={mode === "login" ? "current-password" : "new-password"} />

        {error && <div className="alert error" role="alert">{error}</div>}
        <Button type="submit" disabled={loading}>{loading ? "Aguarde..." : mode === "login" ? "Entrar" : "Salvar e criar perfil"}</Button>
        {mode === "cadastro" && <p className="privacy-note">Você decide o que registrar. O sistema não inventa dados sobre a pessoa.</p>}
      </form>
    </main>
  );
}

function normalizeRoutinePeriod(item) {
  if (["manha", "tarde", "noite"].includes(item?.periodo)) return item.periodo;
  const hour = Number.parseInt(String(item?.horario || "").split(":")[0], 10);
  if (!Number.isNaN(hour)) {
    if (hour >= 12 && hour < 18) return "tarde";
    if (hour >= 18 || hour < 6) return "noite";
  }
  return "manha";
}

function routineVisual(title = "Atividade") {
  const normalized = title.toLowerCase();
  if (normalized.includes("banho") || normalized.includes("lavar")) return "🧼";
  if (normalized.includes("comer") || normalized.includes("café") || normalized.includes("almoço") || normalized.includes("jantar")) return "🍽️";
  if (normalized.includes("vestir") || normalized.includes("roupa")) return "👕";
  if (normalized.includes("escovar") || normalized.includes("dente")) return "🪥";
  if (normalized.includes("escola") || normalized.includes("mochila")) return "🎒";
  if (normalized.includes("dormir") || normalized.includes("noite")) return "🌙";
  if (normalized.includes("brincar")) return "🧩";
  return "⭐";
}

function stepVisual(stepText, taskTitle = "") {
  const text = `${taskTitle} ${stepText}`.toLowerCase();
  if (text.includes("chuveiro") || text.includes("abrir")) return "🚿";
  if (text.includes("sabonete") || text.includes("sabão")) return "🧼";
  if (text.includes("axila")) return "🙆";
  if (text.includes("íntim") || text.includes("partes")) return "🫧";
  if (text.includes("pé")) return "🦶";
  if (text.includes("cabeça") || text.includes("cabelo")) return "🧴";
  if (text.includes("escova") || text.includes("dente")) return "🪥";
  if (text.includes("pasta")) return "🧴";
  if (text.includes("enxaguar") || text.includes("água")) return "💧";
  if (text.includes("roupa") || text.includes("vestir")) return "👕";
  if (text.includes("comer") || text.includes("refeição")) return "🍽️";
  if (text.includes("mochila") || text.includes("escola")) return "🎒";
  if (text.includes("guardar") || text.includes("organizar")) return "🧺";
  if (text.includes("mão") || text.includes("lavar")) return "👐";
  if (text.includes("dormir") || text.includes("cama")) return "🛏️";
  return "⭐";
}

function RoutineView({ tasks, reminders, childName, onToggleStep, onMovePeriod, onCreateTask, onCreateReminder, score = 0 }) {
  const [taskForm, setTaskForm] = useState({ titulo: "", horario: "", periodo: "manha", passos: "" });
  const [reminderForm, setReminderForm] = useState({ mensagem: "", horario: "" });
  const [showTask, setShowTask] = useState(false);
  const [showReminder, setShowReminder] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState(null);
  const done = tasks.filter((task) => task.done).length;
  const percentage = tasks.length ? Math.round((done / tasks.length) * 100) : 0;
  const periods = [{ id: "manha", label: "Manhã", icon: "☀️", description: "começo do dia" }, { id: "tarde", label: "Tarde", icon: "🌤️", description: "meio do dia" }, { id: "noite", label: "Noite", icon: "🌙", description: "hora de descansar" }];
  const selectedTask = tasks.find((task) => task.id === selectedTaskId);
  const selectedSteps = selectedTask ? (selectedTask.steps?.length ? selectedTask.steps : [{ texto: selectedTask.title, concluida: false }]) : [];
  const allStepsDone = selectedSteps.length > 0 && selectedSteps.every((step) => step.concluida);

  async function toggleStep(index) {
    if (!selectedTask) return;
    await onToggleStep(selectedTask.id, index);
  }

  return (
    <div className="stack routine-board-page">
      <div className="page-heading"><div><p className="eyebrow">QUADRO DE ROTINAS</p><h2>O que vamos fazer?</h2><p>{childName ? `A rotina visual de ${childName}.` : "A rotina visual da criança."} Escolha uma atividade e siga os passos.</p></div><Button icon={Printer} onClick={() => window.print()}>Imprimir quadro</Button></div>
      <section className="routine-score-card" aria-labelledby="routine-score-title"><div className="score-symbol" aria-hidden="true">★</div><div className="score-copy"><span id="routine-score-title">Pontos conquistados</span><strong>{score} {score === 1 ? "ponto" : "pontos"}</strong><small>{done} de {tasks.length} atividades feitas</small></div><div className="progress" role="progressbar" aria-label="Progresso da rotina visual" aria-valuemin="0" aria-valuemax="100" aria-valuenow={percentage}><span style={{ width: `${percentage}%` }} /></div></section>
      <div className="routine-board-help" role="status" aria-live="polite"><span aria-hidden="true">👆</span><p><strong>Escolha uma imagem para começar.</strong><small>Abra o quadrinho, faça cada passo e marque quando terminar.</small></p></div>
      <div className="actions-row" aria-label="Ações da rotina"><Button onClick={() => setShowTask((visible) => !visible)} aria-expanded={showTask}>+ Atividade</Button><Button secondary onClick={() => setShowReminder((visible) => !visible)} aria-expanded={showReminder}>+ Lembrete</Button></div>
      {showTask && <Card className="form-card"><form onSubmit={(event) => { event.preventDefault(); onCreateTask({ ...taskForm, passos: taskForm.passos.split("\n").map((texto) => texto.trim()).filter(Boolean).map((texto) => ({ texto, concluida: false })) }); setTaskForm({ titulo: "", horario: "", periodo: "manha", passos: "" }); setShowTask(false); }} className="form-grid"><div className="form-section-heading"><h3>Adicionar atividade com passos</h3><p>Uma linha para cada ação. Exemplo: pegar a escova, colocar pasta, escovar os dentes.</p></div><Field label="O que a criança deve fazer?" value={taskForm.titulo} onChange={(event) => setTaskForm({ ...taskForm, titulo: event.target.value })} required placeholder="Ex.: Escovar os dentes" /><Field label="Passos, um por linha" value={taskForm.passos} onChange={(event) => setTaskForm({ ...taskForm, passos: event.target.value })} multiline placeholder={'Pegar a escova\nColocar a pasta\nEscovar os dentes'} /><div className="two-col"><Field label="Horário (opcional)" type="time" value={taskForm.horario} onChange={(event) => setTaskForm({ ...taskForm, horario: event.target.value })} /><label className="field"><span>Período</span><select value={taskForm.periodo} onChange={(event) => setTaskForm({ ...taskForm, periodo: event.target.value })}><option value="manha">Manhã</option><option value="tarde">Tarde</option><option value="noite">Noite</option></select></label></div><Button type="submit">Adicionar ao quadro</Button></form></Card>}
      {showReminder && <Card className="form-card"><form onSubmit={(event) => { event.preventDefault(); onCreateReminder(reminderForm); setReminderForm({ mensagem: "", horario: "" }); setShowReminder(false); }} className="form-grid"><div className="form-section-heading"><h3>Novo lembrete</h3><p>Uma frase curta para facilitar a consulta.</p></div><Field label="Mensagem" value={reminderForm.mensagem} onChange={(event) => setReminderForm({ ...reminderForm, mensagem: event.target.value })} required placeholder="Ex.: levar fone abafador" /><Field label="Horário" type="time" value={reminderForm.horario} onChange={(event) => setReminderForm({ ...reminderForm, horario: event.target.value })} required /><Button type="submit">Salvar lembrete</Button></form></Card>}

      <section aria-labelledby="routine-board-title"><div className="section-title-row"><div><p className="eyebrow">QUADRO VISUAL</p><h3 id="routine-board-title">Minha sequência do dia</h3></div><span className="steps-counter">{done}/{tasks.length}</span></div><div className="routine-board" role="grid" aria-label="Quadro visual da rotina por período do dia">{periods.map((period) => { const periodTasks = tasks.filter((task) => task.periodo === period.id); return <div className="routine-row" role="row" key={period.id}><div className="period-label" role="rowheader"><span className="period-icon" aria-hidden="true">{period.icon}</span><strong>{period.label}</strong><small>{period.description}</small></div><div className="period-activities" role="gridcell">{periodTasks.length === 0 ? <span className="empty-period">Nenhuma atividade</span> : periodTasks.map((task) => <div className="routine-tile-wrap" key={task.id}><button type="button" className={`routine-tile ${task.done ? "completed" : ""} ${selectedTaskId === task.id ? "selected" : ""}`} onClick={() => setSelectedTaskId(task.id)} aria-pressed={selectedTaskId === task.id} aria-label={`${task.done ? "Abrir atividade concluída" : "Abrir atividade"}: ${task.title}`}>{task.done && <span className="tile-check" aria-hidden="true"><Check size={18} /></span>}<span className="tile-image" role="img" aria-label={`Imagem: ${task.title}`}>{routineVisual(task.title)}</span><strong>{task.title}</strong><small>{task.time || "No seu tempo"}</small><span className="tile-points">{task.done ? "Feito · +10" : `${task.steps?.length || 1} passo${(task.steps?.length || 1) === 1 ? "" : "s"}`}</span></button><label className="tile-move-control"><span className="sr-only">Mover {task.title} para outro período</span><select aria-label={`Mover ${task.title} para outro período`} value={task.periodo} onChange={(event) => onMovePeriod(task.id, event.target.value)}><option value="manha">Manhã</option><option value="tarde">Tarde</option><option value="noite">Noite</option></select></label></div>)}</div></div>})}</div></section>

      {selectedTask && <section className="task-step-board" aria-labelledby="selected-task-title"><div className="task-step-visual" role="img" aria-label={`Imagem da atividade ${selectedTask.title}`}>{routineVisual(selectedTask.title)}</div><div className="task-step-content"><div className="step-detail-heading"><div><p className="eyebrow">ATIVIDADE ESCOLHIDA</p><h3 id="selected-task-title">{selectedTask.title}</h3><p>Faça uma coisa de cada vez. Marque cada passo quando terminar.</p></div><button type="button" className="icon-button" onClick={() => setSelectedTaskId(null)} aria-label="Fechar atividade"><X size={18} aria-hidden="true" /></button></div><ol className="task-step-list">{selectedSteps.map((step, index) => <li className={step.concluida ? "done" : ""} key={`${selectedTask.id}-step-${index}`}><button type="button" className="step-check-button" onClick={() => toggleStep(index)} aria-pressed={Boolean(step.concluida)} aria-label={`${step.concluida ? "Desmarcar" : "Marcar"} passo ${index + 1}: ${step.texto}`}>{step.concluida ? <Check size={18} aria-hidden="true" /> : index + 1}</button><span className="step-visual" role="img" aria-label={`Imagem do passo: ${step.texto}`}>{stepVisual(step.texto, selectedTask.title)}</span><span>{step.texto}</span><small className="step-points">{step.concluida ? "+2 pontos" : "Vale 2 pontos"}</small></li>)}</ol><div className="task-completion-row"><span>{selectedTask.done ? "Atividade concluída! Você fez todos os quadrinhos." : allStepsDone ? "Todos os quadrinhos foram marcados." : "Marque cada quadrinho quando terminar."}</span><strong>{selectedTask.done ? "Concluída" : `${selectedSteps.filter((step) => step.concluida).length} de ${selectedSteps.length} passos · 2 pontos por passo`}</strong></div></div></section>}
      <Card><h3>Lembretes</h3>{reminders.length === 0 ? <Empty>Nenhum lembrete cadastrado.</Empty> : <ul className="reminder-list">{reminders.map((item, index) => <li className="list-line" key={item.id || index}><span className="mini-icon" aria-hidden="true">!</span><span>{item.mensagem}</span><strong>{item.horario || "Sem horário"}</strong></li>)}</ul>}</Card>
    </div>
  );
}

function LibraryView() {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("todos");
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    const timer = window.setTimeout(() => {
      setLoading(true);
      setError("");
      get(`/api/biblioteca?q=${encodeURIComponent(query)}&tipo=${encodeURIComponent(type)}`)
        .then((data) => { if (active) setItems(data); })
        .catch((e) => { if (active) setError(e.message); })
        .finally(() => { if (active) setLoading(false); });
    }, 220);
    return () => { active = false; window.clearTimeout(timer); };
  }, [query, type]);

  const filterTypes = ["todos", "artigo", "livro", "série", "filme"];

  return (
    <div className="stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">CONTEÚDO CONFIÁVEL</p>
          <h2>Biblioteca sobre TEA</h2>
          <p>Pesquise artigos, livros, séries e filmes no seu ritmo.</p>
        </div>
        <BookOpen size={30} color={COLORS.primary} aria-hidden="true" />
      </div>
      <Card>
        <label className="search" htmlFor="library-search">
          <Search size={18} aria-hidden="true" />
          <span className="sr-only">Pesquisar na biblioteca</span>
          <input id="library-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Tema, título ou fonte" />
        </label>
        <div className="chips" role="group" aria-label="Filtrar materiais por tipo">
          {filterTypes.map((item) => (
            <button type="button" key={item} className={type === item ? "active" : ""} onClick={() => setType(item)} aria-pressed={type === item}>
              {item[0].toUpperCase() + item.slice(1)}
            </button>
          ))}
        </div>
      </Card>
      {error && <div className="alert error" role="alert">{error}</div>}
      {loading && <p className="loading-message" role="status" aria-live="polite">Buscando materiais...</p>}
      {selectedItem && <Card className="library-detail" aria-labelledby="library-detail-title"><div className="library-detail-header"><div><p className="eyebrow">DETALHES DO MATERIAL</p><div className="resource-type">{selectedItem.tipo}</div><h3 id="library-detail-title">{selectedItem.titulo}</h3></div><button type="button" className="icon-button" onClick={() => setSelectedItem(null)} aria-label="Fechar detalhes da biblioteca"><X size={18} aria-hidden="true" /></button></div><p className="library-detail-description">{selectedItem.descricao}</p><div className="library-detail-columns"><div><strong>Fonte</strong><span>{selectedItem.fonte || "Biblioteca Atípica"}</span></div><div><strong>Como usar</strong><span>Leia no seu ritmo e escolha uma ideia pequena para experimentar ou conversar com a equipe.</span></div></div><div className="library-detail-actions">{selectedItem.url ? <a className="btn btn-primary" href={selectedItem.url} target="_blank" rel="noreferrer">Abrir arquivo <span aria-hidden="true">↗</span></a> : <span className="library-file-note"><BookOpen size={15} aria-hidden="true" /> Subaba de leitura disponível</span>}<button type="button" className="btn btn-secondary" onClick={() => setSelectedItem(null)}>Voltar para materiais</button></div></Card>}
      <div className="library-grid" aria-live="polite">
        {items.map((item) => (
          <Card key={item.id} as="article" className={selectedItem?.id === item.id ? "resource-selected" : ""}>
            <div className="resource-type">{item.tipo}</div>
            <h3>{item.titulo}</h3>
            <p>{item.descricao}</p>
            <small>{item.fonte}</small>
            <button type="button" className="resource-open" onClick={() => setSelectedItem(item)} aria-label={`Ver detalhes de ${item.titulo}`}>Ver detalhes <span aria-hidden="true">→</span></button>
          </Card>
        ))}
        {!loading && items.length === 0 && <Empty>Nenhum material encontrado. Tente outra palavra ou filtro.</Empty>}
      </div>
      <p className="disclaimer">A biblioteca é informativa. Um material não substitui avaliação ou orientação profissional.</p>
    </div>
  );
}

function AssistantView({ childName, user, onUserChange }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([{ from: "bot", text: `Olá. Posso ajudar a organizar a rotina de ${childName || "quem você acompanha"}. Faça uma pergunta curta.` }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [permissionStatus, setPermissionStatus] = useState("");
  const [savingPermissions, setSavingPermissions] = useState(false);
  const [permissions, setPermissions] = useState(() => ({ perfil: false, preferencias: false, rotina: false, historico: false }));
  const logRef = useRef(null);

  useEffect(() => {
    const saved = user?.preferencias?.ia_permissoes || {};
    setPermissions({ perfil: Boolean(saved.perfil), preferencias: Boolean(saved.preferencias), rotina: Boolean(saved.rotina), historico: Boolean(saved.historico) });
  }, [user]);

  async function savePermissions() {
    setSavingPermissions(true);
    setPermissionStatus("");
    try {
      const updated = await patch(`/api/perfil?email=${encodeURIComponent(currentEmail)}`, { preferencias: { ia_permissoes: permissions } });
      onUserChange(updated);
      setPermissionStatus("Permissões salvas. A alteração vale para as próximas mensagens.");
    } catch (e) {
      setPermissionStatus(e.message || "Não foi possível salvar as permissões.");
    } finally {
      setSavingPermissions(false);
    }
  }

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages, loading]);

  function clearConversation() {
    if (loading) return;
    setMessages([{ from: "bot", text: `Olá. Posso ajudar a organizar a rotina de ${childName || "quem você acompanha"}. Faça uma pergunta curta.` }]);
    setQuestion("");
    setError("");
  }

  async function send() {
    const text = question.trim();
    if (!text || loading) return;
    const historico = messages.slice(1).map((message) => ({
      papel: message.from === "bot" ? "assistente" : "usuario",
      texto: message.text,
    }));
    setMessages((current) => [...current, { from: "user", text }]);
    setQuestion("");
    setLoading(true);
    setError("");
    try {
      const data = await post("/api/assistente", { email: currentEmail, pergunta: text, historico });
      const answer = Array.isArray(data.resposta) ? data.resposta.join("\n") : String(data.resposta || "Sem resposta");
      setMessages((current) => [...current, { from: "bot", text: answer, mode: data.modo, personalized: Boolean(data.dados_autorizados?.length) }]);
    } catch (e) {
      setError(`${e.message}. Verifique se a API está disponível.`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">APOIO À DECISÃO</p>
          <h2>Assistente Atípica</h2>
          <p>Respostas curtas e claras, sem substituir profissionais.</p>
        </div>
          <div className="assistant-actions"><Button secondary icon={RotateCcw} onClick={clearConversation} disabled={loading}>Nova conversa</Button><Bot size={30} color={COLORS.primary} aria-hidden="true" /></div>
      </div>
      <Card className="permission-card" aria-labelledby="ai-permissions-title">
        <div className="permission-heading"><ShieldCheck size={22} color={COLORS.primary} aria-hidden="true" /><div><h3 id="ai-permissions-title">Permissões da IA</h3><p>Escolha quais categorias podem ser usadas para personalizar as próximas respostas. A IA nunca recebe sua senha, chave ou dados de outras pessoas.</p></div></div>
        <div className="permission-options">
          {[{ key: "perfil", label: "Informações do perfil", detail: "Nome e informações da pessoa acompanhada." }, { key: "preferencias", label: "Preferências", detail: "Estilo de comunicação e preferências sensoriais." }, { key: "rotina", label: "Rotina e estudos", detail: "Tarefas, passos, lembretes e estudos." }, { key: "historico", label: "Histórico registrado", detail: "Registros feitos por você no sistema." }].map((item) => <label className="check-option" key={item.key}><input type="checkbox" checked={permissions[item.key]} onChange={(event) => setPermissions((current) => ({ ...current, [item.key]: event.target.checked }))} /><span><strong>{item.label}</strong><small>{item.detail}</small></span></label>)}
        </div>
        <div className="permission-footer"><Button onClick={savePermissions} disabled={savingPermissions}>{savingPermissions ? "Salvando..." : "Salvar permissões"}</Button><span className="assistant-note">{Object.values(permissions).some(Boolean) ? "IA com acesso autorizado às categorias selecionadas." : "IA sem acesso aos dados da sua conta."}</span></div>
        {permissionStatus && <p className="privacy-note" role="status">{permissionStatus}</p>}
      </Card>
      <Card className="chat-card">
        <div className="chat-messages" ref={logRef} role="log" aria-live="polite" aria-label="Conversa com o Assistente Atípica">
          {messages.map((message, index) => {
            const lines = message.text.split("\n");
            return (
              <div key={index} className={`bubble ${message.from}`}>
                {message.mode === "offline" && <small>Modo offline</small>}
                {message.personalized && <small className="personalized-note"><ShieldCheck size={12} aria-hidden="true" /> Resposta personalizada com dados autorizados</small>}
                {lines.map((line, lineIndex) => <React.Fragment key={lineIndex}>{line}{lineIndex < lines.length - 1 && <br />}</React.Fragment>)}
              </div>
            );
          })}
          {loading && <div className="bubble bot" aria-label="O assistente está pensando">Pensando...</div>}
        </div>
        <form className="chat-input" onSubmit={(event) => { event.preventDefault(); send(); }}>
          <label className="sr-only" htmlFor="assistant-question">Pergunta para o assistente</label>
          <input id="assistant-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ex.: Como organizar uma transição?" autoComplete="off" />
          <Button type="submit" icon={Send} disabled={loading}>Enviar</Button>
        </form>
        <p className="assistant-note">Use as respostas como apoio para pensar em possibilidades. Em situações urgentes, procure um serviço de confiança.</p>
        {error && <div className="alert error" role="alert">{error}</div>}
      </Card>
    </div>
  );
}

function ProfileView({ user, onUserChange }) {
  const [form, setForm] = useState({ nome: user.nome || "", nome_crianca: user.nome_crianca || "", ...(user.informacoes_crianca || {}) });
  const [support, setSupport] = useState([]);
  const [interactions, setInteractions] = useState([]);
  const [person, setPerson] = useState({ nome: "", funcao: "", telefone: "", email: "", observacoes: "", tipo: "apoio" });
  const [note, setNote] = useState({ pessoa: "", texto: "", tipo: "apoio" });
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState("");

  async function load() {
    try {
      const [supportData, interactionData] = await Promise.all([
        get(`/api/rede-apoio?email=${encodeURIComponent(currentEmail)}`),
        get(`/api/interacoes?email=${encodeURIComponent(currentEmail)}`),
      ]);
      setSupport(supportData);
      setInteractions(interactionData);
    } catch (e) {
      setMessage(e.message || "Não foi possível carregar a rede de apoio.");
    }
  }

  useEffect(() => { load(); }, []);

  async function saveProfile(event) {
    event.preventDefault();
    setBusy("profile");
    setMessage("");
    try {
      const updated = await patch(`/api/perfil?email=${encodeURIComponent(currentEmail)}`, {
        nome: form.nome,
        nome_crianca: form.nome_crianca,
        informacoes_crianca: { idade: form.idade, comunicacao: form.comunicacao, necessidades: form.necessidades, interesses: form.interesses },
      });
      onUserChange(updated);
      setMessage("Perfil salvo com sucesso.");
    } catch (e) {
      setMessage(e.message || "Não foi possível salvar o perfil.");
    } finally {
      setBusy("");
    }
  }

  async function addPerson(event) {
    event.preventDefault();
    setBusy("person");
    try {
      await post(`/api/rede-apoio?email=${encodeURIComponent(currentEmail)}`, person);
      setPerson({ nome: "", funcao: "", telefone: "", email: "", observacoes: "", tipo: "apoio" });
      await load();
      setMessage("Pessoa adicionada à sua rede.");
    } catch (e) {
      setMessage(e.message || "Não foi possível adicionar essa pessoa.");
    } finally {
      setBusy("");
    }
  }

  async function addInteraction(event) {
    event.preventDefault();
    setBusy("interaction");
    try {
      await post(`/api/interacoes?email=${encodeURIComponent(currentEmail)}`, note);
      setNote({ pessoa: "", texto: "", tipo: "apoio" });
      await load();
      setMessage("Interação registrada.");
    } catch (e) {
      setMessage(e.message || "Não foi possível registrar a interação.");
    } finally {
      setBusy("");
    }
  }

  return (
    <div className="stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">DADOS SOB SEU CONTROLE</p>
          <h2>Perfil e rede de apoio</h2>
          <p>Revise e atualize as informações quando precisar.</p>
        </div>
        <UserRound size={30} color={COLORS.primary} aria-hidden="true" />
      </div>

      {message && <div className="alert feedback" role="status" aria-live="polite">{message}</div>}

      <Card>
        <h3>Informações da pessoa acompanhada</h3>
        <p className="section-description">Registre preferências e formas de apoio que tornam o dia mais previsível e confortável.</p>
        <form onSubmit={saveProfile} className="form-grid">
          <Field label="Nome" value={form.nome_crianca} onChange={(event) => setForm({ ...form, nome_crianca: event.target.value })} required />
          <div className="two-col">
            <Field label="Idade" value={form.idade} onChange={(event) => setForm({ ...form, idade: event.target.value })} />
            <Field label="Comunicação" value={form.comunicacao} onChange={(event) => setForm({ ...form, comunicacao: event.target.value })} />
          </div>
          <Field label="Necessidades de apoio" multiline value={form.necessidades} onChange={(event) => setForm({ ...form, necessidades: event.target.value })} />
          <Field label="Interesses" multiline value={form.interesses} onChange={(event) => setForm({ ...form, interesses: event.target.value })} />
          <Button type="submit" disabled={busy === "profile"}>{busy === "profile" ? "Salvando..." : "Salvar informações"}</Button>
        </form>
      </Card>

      <Card>
        <div className="section-head"><div><h3>Adicionar pessoa</h3><p>Inclua alguém que participa do cuidado, da educação ou da rotina.</p></div><Users size={20} aria-hidden="true" /></div>
        <form onSubmit={addPerson} className="form-grid">
          <div className="two-col"><Field label="Nome" value={person.nome} onChange={(event) => setPerson({ ...person, nome: event.target.value })} required /><Field label="Função ou relação" value={person.funcao} onChange={(event) => setPerson({ ...person, funcao: event.target.value })} /></div>
          <div className="two-col"><Field label="Telefone" value={person.telefone} onChange={(event) => setPerson({ ...person, telefone: event.target.value })} type="tel" /><Field label="E-mail" value={person.email} onChange={(event) => setPerson({ ...person, email: event.target.value })} type="email" /></div>
          <Field label="Observações" value={person.observacoes} onChange={(event) => setPerson({ ...person, observacoes: event.target.value })} multiline />
          <Button type="submit" disabled={busy === "person"}>{busy === "person" ? "Adicionando..." : "Adicionar à rede"}</Button>
        </form>
        {support.length === 0 ? <Empty>Nenhuma pessoa cadastrada ainda.</Empty> : <div className="people-list">{support.map((personItem, index) => <div className="person" key={personItem.id || index}><div><strong>{personItem.nome}</strong><p>{personItem.funcao || "Pessoa de apoio"}</p><small>{personItem.telefone || personItem.email || "Contato não informado"}</small></div></div>)}</div>}
      </Card>

      <Card>
        <div className="section-head"><div><h3>Registrar interação</h3><p>Guarde informações que podem ajudar no próximo encontro.</p></div><MessageCircle size={20} aria-hidden="true" /></div>
        <form onSubmit={addInteraction} className="form-grid">
          <Field label="Pessoa ou profissional" value={note.pessoa} onChange={(event) => setNote({ ...note, pessoa: event.target.value })} required />
          <Field label="Registro" value={note.texto} onChange={(event) => setNote({ ...note, texto: event.target.value })} multiline required />
          <Button type="submit" disabled={busy === "interaction"}>{busy === "interaction" ? "Salvando..." : "Salvar interação"}</Button>
        </form>
        {interactions.length === 0 ? <Empty>Nenhuma interação registrada ainda.</Empty> : interactions.slice(0, 5).map((item, index) => <div className="list-line" key={item.id || index}><MessageCircle size={16} aria-hidden="true" /><span><strong>{item.pessoa}</strong><br />{item.texto}</span><small>{item.data}</small></div>)}
      </Card>
    </div>
  );
}

function communityTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("pt-BR", { hour: "2-digit", minute: "2-digit" }).format(date);
}

function CommunityView() {
  const [conversas, setConversas] = useState([]);
  const [grupos, setGrupos] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState("");
  const [query, setQuery] = useState("");
  const [people, setPeople] = useState([]);
  const [showGroups, setShowGroups] = useState(false);
  const [showNewGroup, setShowNewGroup] = useState(false);
  const [newGroup, setNewGroup] = useState({ nome: "", tema: "apoio", descricao: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadLists() {
    try {
      const [conversationData, groupData] = await Promise.all([
        get(`/api/comunidade/conversas?email=${encodeURIComponent(currentEmail)}`),
        get(`/api/comunidade/grupos?email=${encodeURIComponent(currentEmail)}`),
      ]);
      setConversas(conversationData);
      setGrupos(groupData);
    } catch (e) {
      setError(e.message || "Não foi possível carregar suas conversas.");
    } finally {
      setLoading(false);
    }
  }

  async function openConversation(conversation) {
    try {
      setActiveId(conversation.id);
      setActiveConversation(conversation);
      setMessages(await get(`/api/comunidade/conversas/${encodeURIComponent(conversation.id)}/mensagens?email=${encodeURIComponent(currentEmail)}`));
    } catch (e) {
      setError(e.message || "Não foi possível abrir esta conversa.");
    }
  }

  useEffect(() => { loadLists(); }, []);

  useEffect(() => {
    const timer = window.setTimeout(async () => {
      if (query.trim().length < 2) { setPeople([]); return; }
      try {
        setPeople(await get(`/api/comunidade/usuarios?email=${encodeURIComponent(currentEmail)}&q=${encodeURIComponent(query)}`));
      } catch (e) { setError(e.message || "Não foi possível buscar pessoas."); }
    }, 220);
    return () => window.clearTimeout(timer);
  }, [query]);

  async function startConversation(username) {
    try {
      const conversation = await post(`/api/comunidade/conversas?email=${encodeURIComponent(currentEmail)}`, { usuario: username });
      setQuery("");
      setPeople([]);
      await loadLists();
      openConversation(conversation);
    } catch (e) { setError(e.message || "Não foi possível iniciar a conversa."); }
  }

  async function sendMessage(event) {
    event.preventDefault();
    if (!activeId || !messageText.trim()) return;
    try {
      const message = await post(`/api/comunidade/conversas/${encodeURIComponent(activeId)}/mensagens?email=${encodeURIComponent(currentEmail)}`, { texto: messageText.trim() });
      setMessages((current) => [...current, message]);
      setMessageText("");
      await loadLists();
    } catch (e) { setError(e.message || "Não foi possível enviar a mensagem."); }
  }

  async function toggleGroup(group) {
    try {
      await post(`/api/comunidade/grupos/${encodeURIComponent(group.id)}/participar?email=${encodeURIComponent(currentEmail)}`, {});
      await loadLists();
    } catch (e) { setError(e.message || "Não foi possível atualizar o grupo."); }
  }

  async function createGroup(event) {
    event.preventDefault();
    if (!newGroup.nome.trim()) return;
    try {
      const group = await post(`/api/comunidade/grupos?email=${encodeURIComponent(currentEmail)}`, newGroup);
      setNewGroup({ nome: "", tema: "apoio", descricao: "" });
      setShowNewGroup(false);
      await loadLists();
      openConversation({ id: `grupo-${group.id}`, tipo: "grupo", nome: group.nome, tema: group.tema, participantes: group.membros, ultima_mensagem: "Ainda não há mensagens." });
    } catch (e) { setError(e.message || "Não foi possível criar o grupo."); }
  }

  const initials = (name = "A") => name.slice(0, 1).toUpperCase();

  return (
    <div className="stack community-page">
      <div className="page-heading">
        <div><p className="eyebrow">CONVERSAS COM CUIDADO</p><h2>Comunidade de apoio</h2><p>Um espaço para conversar com calma, encontrar grupos e manter por perto quem faz bem.</p></div>
        <MessageCircle size={30} color={COLORS.primary} aria-hidden="true" />
      </div>
      {error && <div className="alert error" role="alert"><span>{error}</span><button type="button" onClick={() => setError("")} aria-label="Fechar mensagem"><X size={15} aria-hidden="true" /></button></div>}
      <div className="community-guidance"><ShieldCheck size={20} aria-hidden="true" /><p><strong>Converse com segurança.</strong> Não compartilhe dados pessoais, informações de saúde ou imagens de outras pessoas sem consentimento.</p></div>

      <div className="chat-layout">
        <aside className={`chat-sidebar ${activeId ? "has-active" : ""}`} aria-label="Conversas e grupos">
          <div className="chat-sidebar-header"><div><h3>Conversas</h3><span>{conversas.length} conversa{conversas.length === 1 ? "" : "s"}</span></div><button type="button" className="icon-button" onClick={() => setShowNewGroup((value) => !value)} aria-label="Criar grupo" title="Criar grupo"><Users size={18} aria-hidden="true" /></button></div>
          <label className="search chat-search" htmlFor="people-search"><Search size={17} aria-hidden="true" /><span className="sr-only">Buscar pessoa para conversar</span><input id="people-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar pessoa" /></label>
          {people.length > 0 && <div className="people-results" aria-live="polite">{people.map((person) => <button type="button" className="person-result" key={person.usuario} onClick={() => startConversation(person.usuario)}><span className="avatar small" aria-hidden="true">{initials(person.nome_exibicao)}</span><span><strong>{person.nome_exibicao}</strong><small>@{person.usuario}</small></span><MessageCircle size={16} aria-hidden="true" /></button>)}</div>}
          {showNewGroup && <form className="new-group-form" onSubmit={createGroup}><h4>Novo grupo de apoio</h4><Field label="Nome do grupo" value={newGroup.nome} onChange={(event) => setNewGroup({ ...newGroup, nome: event.target.value })} required /><Field label="Tema" value={newGroup.tema} onChange={(event) => setNewGroup({ ...newGroup, tema: event.target.value })} required /><Field label="Descrição" value={newGroup.descricao} onChange={(event) => setNewGroup({ ...newGroup, descricao: event.target.value })} multiline /><Button type="submit">Criar grupo</Button></form>}
          <div className="chat-tabs" role="tablist" aria-label="Conversas ou grupos"><button type="button" role="tab" aria-selected={!showGroups} className={!showGroups ? "active" : ""} onClick={() => setShowGroups(false)}>Conversas</button><button type="button" role="tab" aria-selected={showGroups} className={showGroups ? "active" : ""} onClick={() => setShowGroups(true)}>Grupos</button></div>
          {loading ? <p className="loading-message" role="status">Carregando...</p> : showGroups ? <div className="group-list">{grupos.length === 0 ? <p className="empty-small">Ainda não há grupos. Crie o primeiro espaço de troca.</p> : grupos.map((group) => <div className="group-item" key={group.id}><div className="group-symbol" aria-hidden="true"><Users size={18} /></div><div className="group-info"><strong>{group.nome}</strong><span>{group.membros} membro{group.membros === 1 ? "" : "s"} · {group.tema}</span><small>{group.descricao || "Um espaço para trocar experiências."}</small></div><button type="button" className={`follow-button ${group.participa ? "following" : ""}`} aria-pressed={group.participa} onClick={() => toggleGroup(group)}>{group.participa ? "Abrir" : "Entrar"}</button></div>)}</div> : <div className="conversation-list">{conversas.length === 0 ? <p className="empty-small">Você ainda não iniciou uma conversa. Busque uma pessoa acima.</p> : conversas.map((conversation) => <button type="button" className={`conversation-item ${activeId === conversation.id ? "active" : ""}`} key={conversation.id} onClick={() => openConversation(conversation)}><span className="avatar small" aria-hidden="true">{initials(conversation.nome)}</span><span className="conversation-copy"><strong>{conversation.nome}</strong><small>{conversation.ultima_mensagem}</small></span><time>{communityTime(conversation.ultima_data)}</time></button>)}</div>}
        </aside>

        <section className="chat-panel" aria-label={activeConversation ? `Conversa com ${activeConversation.nome}` : "Área da conversa"}>
          {!activeConversation ? <div className="chat-welcome"><div className="chat-welcome-icon"><MessageCircle size={34} aria-hidden="true" /></div><h3>Escolha uma conversa</h3><p>Busque uma pessoa ou entre em um grupo para começar uma troca no seu ritmo.</p><span>Você decide quando responder e o que compartilhar.</span></div> : <><header className="chat-header"><div className="avatar" aria-hidden="true">{initials(activeConversation.nome)}</div><div><h3>{activeConversation.nome}</h3><span>{activeConversation.tipo === "grupo" ? `${activeConversation.participantes || 0} participantes` : "Conversa privada"}</span></div></header><div className="chat-messages" aria-live="polite">{messages.length === 0 ? <p className="empty-chat">Ainda não há mensagens. Você pode começar com uma saudação simples.</p> : messages.map((message) => <div className={`message-bubble ${message.propria ? "own" : "other"}`} key={message.id}><p>{message.texto}</p><time>{communityTime(message.criado_em)}</time></div>)}</div><form className="chat-composer" onSubmit={sendMessage}><label className="sr-only" htmlFor="chat-message">Escreva uma mensagem</label><textarea id="chat-message" value={messageText} onChange={(event) => setMessageText(event.target.value)} placeholder="Escreva uma mensagem..." rows="1" maxLength={1000} /><Button type="submit" aria-label="Enviar mensagem" disabled={!messageText.trim()}><Send size={17} aria-hidden="true" />Enviar</Button></form></>}
        </section>
      </div>
    </div>
  );
}

function PreferencesPanel({ preferences, setPreferences, onClose }) {
  return (
    <div id="preferences-panel" className="preferences-panel" role="dialog" aria-labelledby="preferences-title">
      <div className="preferences-heading"><div><p className="eyebrow">CONFORTO</p><h2 id="preferences-title">Preferências de leitura</h2></div><button type="button" className="close-button" onClick={onClose} aria-label="Fechar preferências"><X size={18} /></button></div>
      <p>Escolha o que ajuda você a permanecer no seu ritmo.</p>
      <label className="check-option"><input type="checkbox" checked={preferences.largeText} onChange={(event) => setPreferences({ ...preferences, largeText: event.target.checked })} /><span><strong>Texto maior</strong><small>Aumenta o tamanho da leitura.</small></span></label>
      <label className="check-option"><input type="checkbox" checked={preferences.highContrast} onChange={(event) => setPreferences({ ...preferences, highContrast: event.target.checked })} /><span><strong>Mais contraste</strong><small>Reforça bordas e textos importantes.</small></span></label>
      <label className="check-option"><input type="checkbox" checked={preferences.calmMode} onChange={(event) => setPreferences({ ...preferences, calmMode: event.target.checked })} /><span><strong>Modo calmo</strong><small>Reduz transições e efeitos visuais.</small></span></label>
    </div>
  );
}

export default function AtipicaApp() {
  const [user, setUser] = useState(null);
  const [tab, setTab] = useState("inicio");
  const [tasks, setTasks] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [score, setScore] = useState(0);
  const [error, setError] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [preferences, setPreferences] = useState(() => {
    try {
      return { largeText: localStorage.getItem("atipica-large-text") === "true", highContrast: localStorage.getItem("atipica-high-contrast") === "true", calmMode: localStorage.getItem("atipica-calm-mode") === "true" };
    } catch {
      return { largeText: false, highContrast: false, calmMode: false };
    }
  });

  useEffect(() => {
    document.body.classList.toggle("large-text", preferences.largeText);
    document.body.classList.toggle("high-contrast", preferences.highContrast);
    document.body.classList.toggle("calm-mode", preferences.calmMode);
    try {
      localStorage.setItem("atipica-large-text", String(preferences.largeText));
      localStorage.setItem("atipica-high-contrast", String(preferences.highContrast));
      localStorage.setItem("atipica-calm-mode", String(preferences.calmMode));
    } catch {
      // Preferências continuam funcionando mesmo quando o armazenamento não está disponível.
    }
  }, [preferences]);

  async function load(profile = user) {
    if (!profile?.email) return;
    try {
      const [taskData, reminderData] = await Promise.all([
        get(`/api/tarefas?email=${encodeURIComponent(profile.email)}`),
        get(`/api/lembretes?email=${encodeURIComponent(profile.email)}`),
      ]);
      setTasks(taskData.map((item, index) => ({ id: index, title: item.titulo, time: item.horario, periodo: normalizeRoutinePeriod(item), steps: Array.isArray(item.passos) ? item.passos : [], done: Boolean(item.concluida), points: item.pontos || 10 })));
      setReminders(reminderData);
      setScore(Number(profile?.pontuacao || 0));
    } catch (e) {
      setError(e.message || "Não foi possível carregar sua rotina.");
    }
  }

  useEffect(() => {
    if (user) {
      currentEmail = user.email;
      load(user);
    }
  }, [user]);

  if (!user) return <LoginView onSuccess={(profile) => { currentEmail = profile.email; setUser(profile); }} />;

  const moveTask = async (id, periodo) => {
    try {
      await patch(`/api/tarefas/${id}?email=${encodeURIComponent(user.email)}`, { periodo });
      await load(user);
    } catch (e) {
      setError(e.message || "Não foi possível mudar a atividade de turno.");
    }
  };

  const toggleTaskStep = async (id, passo) => {
    try {
      const result = await patch("/api/tarefas/passo", { email: user.email, indice: id, passo });
      if (typeof result.pontuacao === "number") setScore(result.pontuacao);
      await load(user);
    } catch (e) {
      setError(e.message || "Não foi possível marcar este passo.");
    }
  };

  const createTask = async ({ titulo, horario, periodo, passos }) => {
    try {
      await post("/api/tarefas", { email: user.email, titulo, horario, periodo: periodo || "manha", passos: passos || [] });
      await load(user);
    } catch (e) {
      setError(e.message || "Não foi possível criar a atividade.");
    }
  };

  const createReminder = async ({ mensagem, horario }) => {
    try {
      await post("/api/lembretes", { email: user.email, mensagem, horario });
      await load(user);
    } catch (e) {
      setError(e.message || "Não foi possível criar o lembrete.");
    }
  };

  const toggle = async (id) => {
    setTasks((old) => old.map((item) => item.id === id ? { ...item, done: !item.done } : item));
    try {
      const result = await patch("/api/tarefas/concluir", { email: user.email, indice: id });
      if (typeof result.pontuacao === "number") setScore(result.pontuacao);
    } catch (e) {
      setError(e.message || "Não foi possível atualizar a atividade.");
      await load(user);
    }
  };

  const nav = [
    { id: "inicio", label: "Início", icon: Home },
    { id: "rotina", label: "Rotina", icon: Activity },
    { id: "biblioteca", label: "Biblioteca", icon: BookOpen },
    { id: "assistente", label: "Apoio", icon: Bot },
    { id: "comunidade", label: "Comunidade", icon: Heart },
    { id: "perfil", label: "Perfil", icon: UserRound },
  ];

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Pular para o conteúdo principal</a>
      <header className="topbar">
        <div className="brand compact">
          <div className="brand-mark" aria-hidden="true">A</div>
          <div><strong>Atípica</strong><span>{user.nome_crianca ? `Rotina de ${user.nome_crianca}` : "Organização e apoio"}</span></div>
        </div>
        <div className="topbar-actions">
          <button type="button" className="settings-trigger" aria-expanded={settingsOpen} aria-controls="preferences-panel" onClick={() => setSettingsOpen((open) => !open)}><Settings size={18} aria-hidden="true" /><span>Conforto</span><ChevronDown size={15} aria-hidden="true" /></button>
          <button type="button" className="icon-button" title="Sair" aria-label="Sair do perfil" onClick={() => { currentEmail = null; setUser(null); setSettingsOpen(false); }}><LogOut size={18} aria-hidden="true" /></button>
        </div>
        {settingsOpen && <PreferencesPanel id="preferences-panel" preferences={preferences} setPreferences={setPreferences} onClose={() => setSettingsOpen(false)} />}
      </header>

      <main id="main-content" className="content" tabIndex="-1">
        {error && <div className="alert error" role="alert"><span>{error}</span><button type="button" onClick={() => setError("")} aria-label="Fechar mensagem de erro"><X size={15} aria-hidden="true" /></button></div>}
        {tab === "inicio" && <div className="stack">
          <section className="welcome" aria-labelledby="welcome-title">
            <div><p className="eyebrow">UM PASSO DE CADA VEZ</p><h1 id="welcome-title">Olá, {user.nome.split(" ")[0]}.</h1><p>O que ajudaria você e {user.nome_crianca || "a pessoa acompanhada"} hoje?</p></div>
            <div className="welcome-note"><strong>Este espaço é seu.</strong><span>Você pode ajustar a rotina, buscar informação ou apenas registrar como foi o dia.</span></div>
          </section>
          <section className="dashboard-summary" aria-label="Resumo do dia">
            <div className="dashboard-stat"><span className="dashboard-stat-icon" aria-hidden="true"><Activity size={18} /></span><div><small>Rotina de hoje</small><strong>{tasks.filter((task) => task.concluida).length}/{tasks.length}</strong><span>{tasks.length ? "atividades concluídas" : "nenhuma atividade cadastrada"}</span></div></div>
            <div className="dashboard-stat"><span className="dashboard-stat-icon" aria-hidden="true"><Check size={18} /></span><div><small>Pontuação</small><strong>{score}</strong><span>{score === 1 ? "ponto conquistado" : "pontos conquistados"}</span></div></div>
            <div className="dashboard-stat"><span className="dashboard-stat-icon" aria-hidden="true"><ShieldCheck size={18} /></span><div><small>Próximo cuidado</small><strong>{reminders.length}</strong><span>{reminders.length === 1 ? "lembrete ativo" : "lembretes ativos"}</span></div></div>
          </section>
          {!user.nome_crianca && <div className="privacy-note">Complete o nome no Perfil quando se sentir à vontade para organizar os dois ritmos juntos.</div>}
          <section className="tabs-section" aria-labelledby="explore-title">
            <div className="tabs-section-heading"><div><p className="eyebrow">EXPLORE SEU ESPAÇO</p><h2 id="explore-title">Escolha uma área para continuar</h2><p>Você pode entrar em qualquer bloco e voltar quando quiser.</p></div><span className="tabs-section-mark" aria-hidden="true"><span /><span /><span /></span></div>
            <div className="home-grid" role="list">
              <TabCard icon={Activity} label="Organização" title="Rotina" description="Atividades, lembretes e um quadro visual para o dia." indicator={tasks.length ? `${tasks.length} atividades` : "Começar agora"} tone="blue" active={tab === "rotina"} onClick={() => setTab("rotina")} />
              <TabCard icon={Bot} label="Decisão" title="Assistente" description="Orientações claras para pensar nos próximos passos." indicator="Apoio disponível" tone="yellow" active={tab === "assistente"} onClick={() => setTab("assistente")} />
              <TabCard icon={Users} label="Conexão" title="Rede de apoio" description="Contatos e registros compartilhados por você." indicator="Seu espaço" tone="green" active={tab === "perfil"} onClick={() => setTab("perfil")} />
              <TabCard icon={Heart} label="Comunidade" title="Trocas" description="Conversas com pessoas que entendem diferentes vivências." indicator="Conectar" tone="red" active={tab === "comunidade"} onClick={() => setTab("comunidade")} />
              <TabCard icon={BookOpen} label="Informação" title="Biblioteca" description="Conteúdos para explorar no seu tempo e no seu ritmo." indicator="Materiais" tone="blue" active={tab === "biblioteca"} onClick={() => setTab("biblioteca")} />
            </div>
          </section>
        </div>}
        {tab === "rotina" && <RoutineView tasks={tasks} reminders={reminders} childName={user.nome_crianca} score={score} onToggle={toggle} onMovePeriod={moveTask} onToggleStep={toggleTaskStep} onCreateTask={createTask} onCreateReminder={createReminder} />}
        {tab === "biblioteca" && <LibraryView />}
        {tab === "assistente" && <AssistantView childName={user.nome_crianca} user={user} onUserChange={setUser} />}
        {tab === "comunidade" && <CommunityView />}
        {tab === "perfil" && <ProfileView user={user} onUserChange={setUser} />}
      </main>

      <nav className="bottom-nav" aria-label="Navegação principal">
        {nav.map(({ id, label, icon: Icon }) => <button type="button" key={id} className={tab === id ? "active" : ""} onClick={() => { setTab(id); setSettingsOpen(false); }} aria-current={tab === id ? "page" : undefined}><Icon size={19} aria-hidden="true" /><span>{label}</span></button>)}
      </nav>
    </div>
  );
}
