/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.HashMap;

public class fvR
implements aqz {
    protected int o;
    protected HashMap<Integer, Short> ekD;
    protected HashMap<Short, Short> ekE;

    public int d() {
        return this.o;
    }

    public HashMap<Integer, Short> cnR() {
        return this.ekD;
    }

    public HashMap<Short, Short> cnS() {
        return this.ekE;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ekD = null;
        this.ekE = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        int n2 = aqH2.bGI();
        this.ekD = new HashMap(n2);
        for (n = 0; n < n2; ++n) {
            int n3 = aqH2.bGI();
            short s = aqH2.bGG();
            this.ekD.put(n3, s);
        }
        n = aqH2.bGI();
        this.ekE = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            short s = aqH2.bGG();
            short s2 = aqH2.bGG();
            this.ekE.put(s, s2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oyW.d();
    }
}
