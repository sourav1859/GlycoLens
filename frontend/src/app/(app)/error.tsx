"use client";
import { AsyncState } from "../../components/ui/AsyncState";
export default function ErrorPage({ reset }: { reset: () => void }) { return <AsyncState title="This page couldn’t load" message="Your saved records haven’t been changed. Please try again." error retry={reset} />; }
