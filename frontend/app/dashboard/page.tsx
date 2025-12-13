import AuthCheck from "../components/auth-check";

export default async function DashboardPage() {
    return (
        <>
            <AuthCheck />
            <h1>Dashboard</h1>
            <p>Welcome to your dashboard!</p>
        </>
    );
}