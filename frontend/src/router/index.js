import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";

import LoginView from "../views/LoginView.vue";
import PanelView from "../views/PanelView.vue";
import FormularioIPHView from "../views/FormularioIPHView.vue";
import RegistroIPHView from "../views/RegistroIPHView.vue";

const routes = [
  { path: "/login", name: "login", component: LoginView, meta: { publica: true } },
  { path: "/", name: "panel", component: PanelView },
  {
    path: "/registro-iph",
    redirect: (to) => {
      const id = to.query?.ID_IPH || to.query?.id || 1;
      return { name: "formulario-iph", params: { id }, query: to.query };
    },
  },
  {
    path: "/iph/:id/:modulo?",
    name: "formulario-iph",
    component: FormularioIPHView,
    props: (route) => ({
      id: route.params.id,
      modulo: route.params.modulo || null,
    }),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (!to.meta.publica && !auth.estaAutenticado) {
    return { name: "login" };
  }
  if (to.name === "login" && auth.estaAutenticado) {
    return { name: "panel" };
  }
  return true;
});

export default router;
