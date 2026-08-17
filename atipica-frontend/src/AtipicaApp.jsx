import React, { useEffect, useMemo, useState } from "react";
import { Activity, BookOpen, Bot, Check, ChevronLeft, Circle, Clock3, FileText, Home, LogOut, MessageCircle, Printer, Search, Send, Settings, UserRound, Users, X } from "lucide-react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const COLORS = { primary: "#7d2844", ink: "#24303a", muted: "#60707b", bg: "#f7f4ef", card: "#ffffff", line: "#dce4e7", soft: "#edf4f2", accent: "#d97756" };
let currentEmail = null;

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Falha na comunicação com ${path}`);
  return body;
}
const get = (path) => api(path);
const post = (path, body) => api(path, { method: "POST", body: JSON.stringify(body) });
const patch = (path, body) => api(path, { method: "PATCH", body: JSON.stringify(body) });

function Button({ children, secondary = false, type = "button", onClick, disabled = false, icon: Icon }) {
  return <button type={type} onClick={onClick} disabled={disabled} className={`btn ${secondary ? "btn-secondary" : "btn-primary"}`}>
    {Icon && <Icon size={17} aria-hidden="true" />}{children}
  </button>;
}
function Field({ label, value, onChange, multiline = false, ...props }) {
  const Tag = multiline ? "textarea" : "input";
  return <label className="field"><span>{label}</span><Tag value={value ?? ""} onChange={onChange} {...props} /></label>;
}
function Card({ children, className = "" }) { return <section className={`card ${className}`}>{children}</section>; }
function Empty({ children }) { return <p className="empty">{children}</p>; }

function LoginView({ onSuccess }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ nome: "", nome_crianca: "", email: "", senha: "", idade_crianca: "", comunicacao_crianca: "", necessidades_crianca: "", interesses_crianca: "" });
  const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  const set = (key) => (event) => setForm((old) => ({ ...old, [key]: event.target.value }));
  async function submit(event) {
    event.preventDefault(); setLoading(true); setError("");
    try { const profile = await post(`/api/${mode === "login" ? "login" : "cadastro"}`, mode === "login" ? { email: form.email, senha: form.senha } : form); onSuccess(profile); }
    catch (e) { setError(e.message || "Não foi possível concluir a operação."); }
    finally { setLoading(false); }
  }
  return <main className="auth-page"><form className="auth-card" onSubmit={submit}>
    <div className="brand"><div className="brand-mark">A</div><div><h1>Atípica</h1><p>Rotina, cuidado e informação com clareza.</p></div></div>
    <div className="switcher"><button type="button" className={mode === "login" ? "selected" : ""} onClick={() => setMode("login")}>Entrar</button><button type="button" className={mode === "cadastro" ? "selected" : ""} onClick={() => setMode("cadastro")}>Criar perfil</button></div>
    {mode === "cadastro" && <><Field label="Nome do responsável" value={form.nome} onChange={set("nome")} required placeholder="Como devemos chamar você?" /><Field label="Nome da criança" value={form.nome_crianca} onChange={set("nome_crianca")} required placeholder="Informado pela família" /><div className="two-col"><Field label="Idade" value={form.idade_crianca} onChange={set("idade_crianca")} placeholder="Ex.: 8 anos" /><Field label="Comunicação" value={form.comunicacao_crianca} onChange={set("comunicacao_crianca")} placeholder="Ex.: fala, CAA..." /></div><Field label="Necessidades de apoio" value={form.necessidades_crianca} onChange={set("necessidades_crianca")} multiline placeholder="Conte o que é importante para a rotina." /><Field label="Interesses" value={form.interesses_crianca} onChange={set("interesses_crianca")} multiline placeholder="Atividades, temas ou objetos de interesse." /></>}
    <Field label="E-mail" value={form.email} onChange={set("email")} type="email" required placeholder="seu@email.com" /><Field label="Senha" value={form.senha} onChange={set("senha")} type="password" minLength={mode === "cadastro" ? 6 : undefined} required placeholder="Mínimo de 6 caracteres" />
    {error && <div className="alert error" role="alert">{error}</div>}<Button type="submit" disabled={loading}>{loading ? "Aguarde..." : mode === "login" ? "Entrar" : "Salvar e criar perfil"}</Button>
    {mode === "cadastro" && <p className="privacy-note">Você controla as informações. O sistema não inventa dados sobre a criança.</p>}
  </form></main>;
}

function RoutineView({ tasks, reminders, childName, onToggle, onCreateTask, onCreateReminder }) {
  const [taskForm, setTaskForm] = useState({ titulo: "", horario: "" }); const [reminderForm, setReminderForm] = useState({ mensagem: "", horario: "" });
  const [showTask, setShowTask] = useState(false); const [showReminder, setShowReminder] = useState(false);
  const done = tasks.filter((task) => task.done).length;
  return <div className="stack">
    <div className="page-heading"><div><p className="eyebrow">ROTINA VISUAL</p><h2>Rotina de {childName || "sua criança"}</h2><p>{done} de {tasks.length} atividades concluídas</p></div><Button icon={Printer} onClick={() => window.print()}>Imprimir</Button></div>
    <Card><div className="progress-row"><strong>{tasks.length ? Math.round(done / tasks.length * 100) : 0}%</strong><span>progresso do dia</span></div><div className="progress"><span style={{ width: `${tasks.length ? done / tasks.length * 100 : 0}%` }} /></div></Card>
    <div className="actions-row"><Button onClick={() => setShowTask((x) => !x)}>+ Atividade</Button><Button secondary onClick={() => setShowReminder((x) => !x)}>+ Lembrete</Button></div>
    {showTask && <Card><form onSubmit={(e) => { e.preventDefault(); onCreateTask(taskForm); setTaskForm({ titulo: "", horario: "" }); setShowTask(false); }} className="form-grid"><Field label="Atividade" value={taskForm.titulo} onChange={(e) => setTaskForm({ ...taskForm, titulo: e.target.value })} required /><Field label="Horário" type="time" value={taskForm.horario} onChange={(e) => setTaskForm({ ...taskForm, horario: e.target.value })} /><Button type="submit">Salvar atividade</Button></form></Card>}
    {showReminder && <Card><form onSubmit={(e) => { e.preventDefault(); onCreateReminder(reminderForm); setReminderForm({ mensagem: "", horario: "" }); setShowReminder(false); }} className="form-grid"><Field label="Mensagem" value={reminderForm.mensagem} onChange={(e) => setReminderForm({ ...reminderForm, mensagem: e.target.value })} required /><Field label="Horário" type="time" value={reminderForm.horario} onChange={(e) => setReminderForm({ ...reminderForm, horario: e.target.value })} required /><Button type="submit">Salvar lembrete</Button></form></Card>}
    <Card><h3>Atividades do dia</h3><div className="task-list">{tasks.length === 0 ? <Empty>Nenhuma atividade cadastrada.</Empty> : tasks.map((task) => <button className={`task ${task.done ? "done" : ""}`} key={task.id} onClick={() => onToggle(task.id)}><span>{task.done ? <Check size={20} /> : <Circle size={20} />}</span><span className="task-text">{task.title}</span><span className="time"><Clock3 size={14} />{task.time || "Sem horário"}</span></button>)}</div></Card>
    <Card><h3>Lembretes</h3>{reminders.length === 0 ? <Empty>Nenhum lembrete cadastrado.</Empty> : reminders.map((item, index) => <div className="list-line" key={index}><BellIcon /><span>{item.mensagem}</span><strong>{item.horario}</strong></div>)}</Card>
  </div>;
}
function BellIcon() { return <span className="mini-icon" aria-hidden="true">!</span>; }

function LibraryView() {
  const [query, setQuery] = useState(""); const [type, setType] = useState("todos"); const [items, setItems] = useState([]); const [error, setError] = useState("");
  useEffect(() => { get(`/api/biblioteca?q=${encodeURIComponent(query)}&tipo=${encodeURIComponent(type)}`).then(setItems).catch((e) => setError(e.message)); }, [query, type]);
  return <div className="stack"><div className="page-heading"><div><p className="eyebrow">CONTEÚDO CONFIÁVEL</p><h2>Biblioteca sobre TEA</h2><p>Pesquise artigos, livros, séries e filmes.</p></div><BookOpen size={30} color={COLORS.primary} /></div><Card><label className="search"><Search size={18} /><input aria-label="Pesquisar na biblioteca" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Pesquisar por tema, título ou fonte" /></label><div className="chips">{["todos", "artigo", "livro", "série", "filme"].map((item) => <button key={item} className={type === item ? "active" : ""} onClick={() => setType(item)}>{item[0].toUpperCase() + item.slice(1)}</button>)}</div></Card>{error && <div className="alert error">{error}</div>}<div className="library-grid">{items.map((item) => <Card key={item.id}><div className="resource-type">{item.tipo}</div><h3>{item.titulo}</h3><p>{item.descricao}</p><small>{item.fonte}</small></Card>)}{items.length === 0 && <Empty>Nenhum material encontrado. Tente outra palavra.</Empty>}</div><p className="disclaimer">A biblioteca é informativa. Um material não substitui avaliação ou orientação profissional.</p></div>;
}

function AssistantView({ childName }) {
  const [question, setQuestion] = useState(""); const [messages, setMessages] = useState([{ from: "bot", text: `Olá. Posso ajudar a organizar a rotina de ${childName || "sua criança"}. Faça uma pergunta curta.` }]); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  async function send() { const text = question.trim(); if (!text || loading) return; setMessages((m) => [...m, { from: "user", text }]); setQuestion(""); setLoading(true); setError(""); try { const data = await post("/api/assistente", { email: currentEmail, pergunta: text }); const answer = Array.isArray(data.resposta) ? data.resposta.join("\n") : String(data.resposta || "Sem resposta"); setMessages((m) => [...m, { from: "bot", text: answer, mode: data.modo }]); } catch (e) { setError(`${e.message}. Verifique se a API está em http://127.0.0.1:8000.`); } finally { setLoading(false); } }
  return <div className="stack"><div className="page-heading"><div><p className="eyebrow">APOIO À DECISÃO</p><h2>Assistente Atípica</h2><p>Respostas curtas, claras e sem substituir profissionais.</p></div><Bot size={30} color={COLORS.primary} /></div><Card className="chat-card"><div className="chat-messages">{messages.map((m, i) => <div key={i} className={`bubble ${m.from}`}>{m.mode === "offline" && <small>Modo offline</small>}{m.text.split("\n").map((line, j) => <React.Fragment key={j}>{line}{j < m.text.split("\n").length - 1 && <br />}</React.Fragment>)}</div>)}{loading && <div className="bubble bot">Pensando...</div>}</div><div className="chat-input"><input aria-label="Pergunta para o assistente" value={question} onChange={(e) => setQuestion(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder="Ex.: Como organizar uma transição?" /><Button icon={Send} onClick={send} disabled={loading}>Enviar</Button></div>{error && <div className="alert error" role="alert">{error}</div>}</Card></div>;
}

function ProfileView({ user, onUserChange }) {
  const [form, setForm] = useState({ nome: user.nome || "", nome_crianca: user.nome_crianca || "", ...(user.informacoes_crianca || {}) }); const [support, setSupport] = useState([]); const [interactions, setInteractions] = useState([]); const [person, setPerson] = useState({ nome: "", funcao: "", telefone: "", email: "", observacoes: "", tipo: "apoio" }); const [note, setNote] = useState({ pessoa: "", texto: "", tipo: "apoio" }); const [message, setMessage] = useState("");
  const load = () => { get(`/api/rede-apoio?email=${encodeURIComponent(currentEmail)}`).then(setSupport).catch(() => {}); get(`/api/interacoes?email=${encodeURIComponent(currentEmail)}`).then(setInteractions).catch(() => {}); };
  useEffect(load, []);
  async function saveProfile(e) { e.preventDefault(); const updated = await patch(`/api/perfil?email=${encodeURIComponent(currentEmail)}`, { nome: form.nome, nome_crianca: form.nome_crianca, informacoes_crianca: { idade: form.idade, comunicacao: form.comunicacao, necessidades: form.necessidades, interesses: form.interesses } }); onUserChange(updated); setMessage("Perfil salvo."); }
  async function addPerson(e) { e.preventDefault(); await post(`/api/rede-apoio?email=${encodeURIComponent(currentEmail)}`, person); setPerson({ nome: "", funcao: "", telefone: "", email: "", observacoes: "", tipo: "apoio" }); load(); }
  async function addInteraction(e) { e.preventDefault(); await post(`/api/interacoes?email=${encodeURIComponent(currentEmail)}`, note); setNote({ pessoa: "", texto: "", tipo: "apoio" }); load(); }
  return <div className="stack"><div className="page-heading"><div><p className="eyebrow">DADOS SOB SEU CONTROLE</p><h2>Perfil e rede de apoio</h2><p>Revise e atualize as informações quando precisar.</p></div><UserRound size={30} color={COLORS.primary} /></div><Card><h3>Informações da criança</h3><form onSubmit={saveProfile} className="form-grid"><Field label="Nome da criança" value={form.nome_crianca} onChange={(e) => setForm({ ...form, nome_crianca: e.target.value })} required /><div className="two-col"><Field label="Idade" value={form.idade} onChange={(e) => setForm({ ...form, idade: e.target.value })} /><Field label="Comunicação" value={form.comunicacao} onChange={(e) => setForm({ ...form, comunicacao: e.target.value })} /></div><Field label="Necessidades de apoio" multiline value={form.necessidades} onChange={(e) => setForm({ ...form, necessidades: e.target.value })} /><Field label="Interesses" multiline value={form.interesses} onChange={(e) => setForm({ ...form, interesses: e.target.value })} /><Button type="submit">Salvar informações</Button>{message && <p className="success">{message}</p>}</form></Card><Card><div className="section-head"><h3>Adicionar pessoa</h3><Users size={20} /></div><form onSubmit={addPerson} className="form-grid"><div className="two-col"><Field label="Nome" value={person.nome} onChange={(e) => setPerson({ ...person, nome: e.target.value })} required /><Field label="Função ou relação" value={person.funcao} onChange={(e) => setPerson({ ...person, funcao: e.target.value })} /></div><div className="two-col"><Field label="Telefone" value={person.telefone} onChange={(e) => setPerson({ ...person, telefone: e.target.value })} /><Field label="E-mail" value={person.email} onChange={(e) => setPerson({ ...person, email: e.target.value })} /></div><Field label="Observações" value={person.observacoes} onChange={(e) => setPerson({ ...person, observacoes: e.target.value })} multiline /><Button type="submit">Adicionar à rede</Button></form>{support.length === 0 ? <Empty>Nenhuma pessoa cadastrada ainda.</Empty> : <div className="people-list">{support.map((p, i) => <div className="person" key={p.id || i}><div><strong>{p.nome}</strong><p>{p.funcao || "Pessoa de apoio"}</p><small>{p.telefone || p.email || "Contato não informado"}</small></div></div>)}</div>}</Card><Card><div className="section-head"><h3>Registrar interação</h3><MessageCircle size={20} /></div><form onSubmit={addInteraction} className="form-grid"><Field label="Pessoa ou profissional" value={note.pessoa} onChange={(e) => setNote({ ...note, pessoa: e.target.value })} required /><Field label="Registro" value={note.texto} onChange={(e) => setNote({ ...note, texto: e.target.value })} multiline required /><Button type="submit">Salvar interação</Button></form>{interactions.slice(0, 5).map((item, i) => <div className="list-line" key={i}><MessageCircle size={16} /><span><strong>{item.pessoa}</strong><br />{item.texto}</span><small>{item.data}</small></div>)}</Card></div>;
}

export default function AtipicaApp() {
  const [user, setUser] = useState(null); const [tab, setTab] = useState("inicio"); const [tasks, setTasks] = useState([]); const [reminders, setReminders] = useState([]); const [error, setError] = useState("");
  const load = async (profile = user) => { if (!profile?.email) return; try { const [taskData, reminderData] = await Promise.all([get(`/api/tarefas?email=${encodeURIComponent(profile.email)}`), get(`/api/lembretes?email=${encodeURIComponent(profile.email)}`)]); setTasks(taskData.map((x, i) => ({ id: i, title: x.titulo, time: x.horario, done: !!x.concluida }))); setReminders(reminderData); } catch (e) { setError(e.message); } };
  useEffect(() => { if (user) { currentEmail = user.email; load(user); } }, [user]);
  if (!user) return <LoginView onSuccess={(profile) => { currentEmail = profile.email; setUser(profile); }} />;
  const createTask = async ({ titulo, horario }) => { await post("/api/tarefas", { email: currentEmail, titulo, horario }); load(); };
  const createReminder = async ({ mensagem, horario }) => { await post("/api/lembretes", { email: currentEmail, mensagem, horario }); load(); };
  const toggle = async (id) => { setTasks((old) => old.map((x) => x.id === id ? { ...x, done: !x.done } : x)); try { await patch("/api/tarefas/concluir", { email: currentEmail, indice: id }); } catch (e) { setError(e.message); load(); } };
  const nav = [{ id: "inicio", label: "Início", icon: Home }, { id: "rotina", label: "Rotina", icon: Activity }, { id: "biblioteca", label: "Biblioteca", icon: BookOpen }, { id: "assistente", label: "IA", icon: Bot }, { id: "perfil", label: "Perfil", icon: UserRound }];
  return    <div className="app-shell"><header className="topbar"><div className="brand compact"><div className="brand-mark">A</div><div><strong>Atípica</strong><span>{user.nome_crianca ? `Rotina de ${user.nome_crianca}` : "Organização e apoio"}</span></div></div><button className="icon-button" title="Sair" aria-label="Sair" onClick={() => { currentEmail = null; setUser(null); }}><LogOut size={18} /></button></header><main className="content">{error && <div className="alert error">{error}<button onClick={() => setError("")}><X size={15} /></button></div>}{tab === "inicio" && <div className="stack"><div className="welcome"><p className="eyebrow">BEM-VINDA(O)</p><h1>Olá, {user.nome.split(" ")[0]}.</h1><p>O que você precisa organizar hoje?</p></div><div className="home-grid"><Card><Activity size={24} color={COLORS.primary} /><h3>Rotina</h3><p>Atividades, lembretes e impressão.</p><Button onClick={() => setTab("rotina")}>Abrir rotina</Button></Card><Card><Bot size={24} color={COLORS.primary} /><h3>Assistente</h3><p>Orientações em linguagem simples.</p><Button onClick={() => setTab("assistente")}>Conversar</Button></Card><Card><Users size={24} color={COLORS.primary} /><h3>Rede de apoio</h3><p>Contatos e registros compartilhados por você.</p><Button onClick={() => setTab("perfil")}>Gerenciar</Button></Card><Card><BookOpen size={24} color={COLORS.primary} /><h3>Biblioteca</h3><p>Artigos, livros, séries e filmes sobre TEA.</p><Button onClick={() => setTab("biblioteca")}>Pesquisar</Button></Card></div></div>}{tab === "rotina" && <RoutineView tasks={tasks} reminders={reminders} childName={user.nome_crianca} onToggle={toggle} onCreateTask={createTask} onCreateReminder={createReminder} />}{tab === "biblioteca" && <LibraryView />}{tab === "assistente" && <AssistantView childName={user.nome_crianca} />}{tab === "perfil" && <ProfileView user={user} onUserChange={setUser} />}</main><nav className="bottom-nav" aria-label="Navegação principal">{nav.map(({ id, label, icon: Icon }) => <button key={id} className={tab === id ? "active" : ""} onClick={() => setTab(id)} aria-current={tab === id ? "page" : undefined}><Icon size={19} /><span>{label}</span></button>)}</nav></div>;
}