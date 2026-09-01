import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import Home from "@/pages/Home";
import Routine from "@/pages/Routine";
import Library from "@/pages/Library";
import Support from "@/pages/Support";
import Profile from "@/pages/Profile";
import SupportNetwork from "@/pages/SupportNetwork";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";

function Router() {
  return <Switch><Route path="/" component={Home} /><Route path="/rotina" component={Routine} /><Route path="/biblioteca" component={Library} /><Route path="/apoio" component={Support} /><Route path="/rede-de-apoio" component={SupportNetwork} /><Route path="/perfil" component={Profile} /><Route path="/404" component={NotFound} /><Route component={NotFound} /></Switch>;
}

export default function App() {
  return <ErrorBoundary><ThemeProvider defaultTheme="light"><TooltipProvider><Toaster /><Router /></TooltipProvider></ThemeProvider></ErrorBoundary>;
}
