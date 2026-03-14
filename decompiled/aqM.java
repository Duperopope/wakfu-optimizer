/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  gnu.trove.impl.hash.TLongHash
 */
import gnu.trove.impl.hash.TLongHash;

public abstract class aqM<Hash extends TLongHash> {
    public final String cRh;
    protected final Hash cRi;

    protected aqM(aqH aqH2) {
        this.cRh = aqH2.bGL().intern();
        int n = aqH2.bGI();
        this.cRi = this.tF(n);
        for (int i = 0; i < n; ++i) {
            long l = aqH2.bGK();
            this.a(l, aqH2);
        }
    }

    public static aqM b(aqH aqH2) {
        boolean bl;
        boolean bl2 = bl = aqH2.aTf() != 0;
        if (bl) {
            return new aqO(aqH2);
        }
        return new aqN(aqH2);
    }

    protected abstract Hash tF(int var1);

    protected abstract void a(long var1, aqH var3);

    public abstract int gw(long var1);

    public abstract int p(long var1, int var3);
}
