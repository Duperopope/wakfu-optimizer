import { BuildProvider } from "@/lib/BuildContext";
import { BuilderLayout } from "@/components/builder/BuilderLayout";

export default function Home() {
  return (
    <BuildProvider>
      <BuilderLayout />
    </BuildProvider>
  );
}
