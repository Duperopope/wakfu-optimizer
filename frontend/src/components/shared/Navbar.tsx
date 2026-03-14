"use client";

import Link from "next/link";
import {
  Languages,
  User,
  Copy,
} from "lucide-react";

function WakfuLogo() {
  return (
    <svg width="30" height="34" viewBox="0 0 30 34" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g clipPath="url(#logo-clip)">
        <path d="M12.852 30.999c-1.838 1.164-9.56 4.943-11.418 1.742-2.065-3.554-1.66-4.264-.295-4.414 1.242-.136 7.347.968 10.431 1.054a3.8 3.8 0 0 0 1.282 1.617" fill="url(#logo-g1)" />
        <path d="M12.16 25.479a3.8 3.8 0 0 0-.83 1.816c-2.676-.126-8.236-.797-9.786-4.167-1.808-3.933-1.156-10.851.819-13.562a.974.974 0 0 1 1.596.03c3.036 4.484 2.62 10.42 8.2 15.883" fill="url(#logo-g2)" />
        <path d="M28.567 32.741c-1.86 3.2-9.58-.578-11.42-1.742a3.8 3.8 0 0 0 1.283-1.618c3.085-.085 9.19-1.19 10.432-1.054 1.364.15 1.77.86-.295 4.414" fill="url(#logo-g3)" />
        <path d="M28.456 23.128c-1.55 3.37-7.11 4.041-9.786 4.167a3.8 3.8 0 0 0-.83-1.816c5.582-5.464 5.165-11.4 8.201-15.883a.974.974 0 0 1 1.596-.03c1.975 2.71 2.628 9.63.82 13.562" fill="url(#logo-g4)" />
        <path d="M16.067 24.299a3.65 3.65 0 0 0-2.134 0c-1.906-6.44-5.286-20.184-.632-23.727a2.804 2.804 0 0 1 3.398 0c4.654 3.543 1.275 17.286-.632 23.727" fill="url(#logo-g5)" />
        <path d="M15 32.185c2.324 0 4.207-1.911 4.207-4.269S17.324 23.648 15 23.648s-4.207 1.91-4.207 4.268 1.884 4.27 4.207 4.27" fill="url(#logo-g6)" />
      </g>
      <defs>
        <linearGradient id="logo-g1" x1="6.426" y1="31.564" x2="6.426" y2="4.007" gradientUnits="userSpaceOnUse">
          <stop stopColor="#71F2FF" /><stop offset="1" stopColor="#29FFE5" />
        </linearGradient>
        <linearGradient id="logo-g2" x1="6.321" y1="31.564" x2="6.321" y2="4.008" gradientUnits="userSpaceOnUse">
          <stop stopColor="#71F2FF" /><stop offset="1" stopColor="#29FFE5" />
        </linearGradient>
        <linearGradient id="logo-g3" x1="23.574" y1="31.564" x2="23.574" y2="4.007" gradientUnits="userSpaceOnUse">
          <stop stopColor="#71F2FF" /><stop offset="1" stopColor="#29FFE5" />
        </linearGradient>
        <linearGradient id="logo-g4" x1="23.679" y1="31.564" x2="23.679" y2="4.008" gradientUnits="userSpaceOnUse">
          <stop stopColor="#71F2FF" /><stop offset="1" stopColor="#29FFE5" />
        </linearGradient>
        <linearGradient id="logo-g5" x1="15" y1="31.564" x2="15" y2="4.007" gradientUnits="userSpaceOnUse">
          <stop stopColor="#71F2FF" /><stop offset="1" stopColor="#29FFE5" />
        </linearGradient>
        <linearGradient id="logo-g6" x1="15" y1="31.564" x2="15" y2="4.008" gradientUnits="userSpaceOnUse">
          <stop stopColor="#E1FFFF" /><stop offset="1" stopColor="#29FFE5" />
        </linearGradient>
        <clipPath id="logo-clip"><path fill="#fff" d="M0 0h30v34H0z" /></clipPath>
      </defs>
    </svg>
  );
}

function DiscordIcon() {
  return (
    <svg width="38" height="30" viewBox="0 0 38 30" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-8 w-8">
      <path d="M32.016 3.17C29.552 2.043 26.951 1.241 24.28.79c-.365.654-.696 1.326-.991 2.015a25.7 25.7 0 0 0-8.586 0A18 18 0 0 0 13.71.79C11.037 1.246 8.435 2.048 5.968 3.176 1.072 10.42-.255 17.484.408 24.448A26.3 26.3 0 0 0 9.897 29.21c.769-1.033 1.448-2.13 2.033-3.277a16.5 16.5 0 0 1-3.2-1.537c.269-.195.531-.395.785-.6 6.007 2.825 12.962 2.825 18.97 0 .257.21.52.41.786.6a16.5 16.5 0 0 1-3.202 1.54 19 19 0 0 0 2.033 3.274 26.2 26.2 0 0 0 9.495-4.76c.779-8.076-1.331-15.076-5.576-21.28ZM12.771 20.165c-1.849 0-3.378-1.679-3.378-3.742s1.475-3.758 3.371-3.758 3.414 1.693 3.38 3.758c-.033 2.065-1.49 3.742-3.373 3.742Zm12.459 0c-1.853 0-3.374-1.679-3.374-3.742s1.475-3.758 3.374-3.758c1.898 0 3.404 1.693 3.371 3.758-.033 2.065-1.485 3.742-3.371 3.742Z" fill="currentColor" />
    </svg>
  );
}

export function Navbar() {
  return (
    <nav className="flex h-[50px] items-center justify-between bg-bg-light p-4">
      <div className="flex items-center gap-16">
        <Link
          href="/"
          className="ml-8 text-2xl flex gap-2 font-bold items-center cursor-pointer text-cyan-wakfuli font-bagnard"
        >
          <WakfuLogo />
          WAKFU OPTIMIZER
        </Link>
        <Link
          href="/builder"
          className="relative flex items-center justify-center text-base font-bold text-primary/75 transition-colors hover:text-primary"
        >
          BUILDER
        </Link>
      </div>
      <div className="flex items-center gap-8">
        <button className="cursor-pointer flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-wakfuli/10 to-cyan-wakfuli/5 border border-cyan-wakfuli/30 hover:border-cyan-wakfuli/60 transition-all duration-200 text-cyan-wakfuli font-semibold text-sm">
          <span className="text-xs opacity-75">Code createur</span>
          <span className="tracking-wider">CUSTOM</span>
          <Copy className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" />
        </button>
        <button className="cursor-pointer h-8 w-8 items-center justify-center rounded-full text-primary/75 transition-colors hover:text-primary">
          <Languages />
        </button>
        <Link
          href="https://discord.gg/your-server"
          target="_blank"
          className="relative flex items-center justify-center text-base font-bold text-primary/75 transition-colors hover:text-primary"
        >
          <DiscordIcon />
        </Link>
        <button className="cursor-pointer flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary transition-colors hover:bg-primary/20">
          <User />
        </button>
      </div>
    </nav>
  );
}
