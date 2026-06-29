import { Routes, Route } from "react-router-dom";

// Páginas serão adicionadas conforme os módulos forem implementados:
// /eventos, /convidados, /confirmar/:token, /mesas, /presentes,
// /fornecedores, /cronograma, /cerimonial, /playlist, /avisos, /mural

function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <h1 className="text-2xl font-semibold">celebra-15</h1>
    </div>
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  );
}
