import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export type User = {
  id: string;
  email: string;
  user_metadata?: {
    display_name?: string;
    first_name?: string;
    last_name?: string;
  };
};

export type AuthError = {
  message: string;
  status?: number;
};

export interface AuthResponse {
  user: User | null;
  session: any | null;
  error: AuthError | null;
}

export interface SignUpData {
  email: string;
  password: string;
  display_name: string;
}

export interface SignInData {
  email: string;
  password: string;
}

// Auth functions
export async function signUp({
  email,
  password,
  display_name,
}: SignUpData): Promise<AuthResponse> {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          display_name,
        },
      },
    });

    if (error) {
      return { user: null, session: null, error: { message: error.message } };
    }

    return {
      user: data.user as User,
      session: data.session,
      error: null,
    };
  } catch (error) {
    return {
      user: null,
      session: null,
      error: { message: "An unexpected error occurred" },
    };
  }
}

export async function signIn({
  email,
  password,
}: SignInData): Promise<AuthResponse> {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      return { user: null, session: null, error: { message: error.message } };
    }

    return {
      user: data.user as User,
      session: data.session,
      error: null,
    };
  } catch (error) {
    return {
      user: null,
      session: null,
      error: { message: "An unexpected error occurred" },
    };
  }
}

export async function signOut() {
  try {
    const { error } = await supabase.auth.signOut();
    if (error) {
      console.error("Error signing out:", error.message);
    }
  } catch (error) {
    console.error("Unexpected error during sign out:", error);
  }
}

export async function getCurrentUser() {
  try {
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser();
    if (error) {
      console.error("Error getting current user:", error.message);
      return null;
    }
    return user as User | null;
  } catch (error) {
    console.error("Unexpected error getting current user:", error);
    return null;
  }
}

export async function getCurrentSession() {
  try {
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();
    if (error) {
      console.error("Error getting current session:", error.message);
      return null;
    }
    return session;
  } catch (error) {
    console.error("Unexpected error getting current session:", error);
    return null;
  }
}
