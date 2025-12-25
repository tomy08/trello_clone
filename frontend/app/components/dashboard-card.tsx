type DashboardCardProps = {
    title?: string;
    cardCount?: number;
    link?: string;
};

export default function DashboardCard({ title, cardCount, link }: DashboardCardProps) {
  return (
    <a href={link} className="bg-white rounded-lg p-6 cursor-pointer hover:shadow-lg transition-all duration-200 hover:-translate-y-1 border border-slate-200 shadow-sm">
      <h3 className="text-slate-800 text-xl font-semibold mb-16">
        {title}
      </h3>
      <p className="text-slate-500 text-sm">{cardCount} cards</p>
    </a>
  );
}
